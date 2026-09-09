<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'

const props = withDefaults(defineProps<{
  width?: string
  height?: string
}>(), {
  width: '100%',
  height: '100%'
})

const containerRef = ref<HTMLDivElement | null>(null)
let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let renderer: THREE.WebGLRenderer | null = null
let animId: number | null = null
let graphGroup: THREE.Group | null = null

let isDragging = false
let prevMousePos = { x: 0, y: 0 }
let targetRotation = { x: 0.2, y: 0.3 }
let currentRotation = { x: 0.2, y: 0.3 }

onMounted(() => {
  if (!containerRef.value) return
  const container = containerRef.value
  const w = container.clientWidth || 450
  const h = container.clientHeight || 340

  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(40, w / h, 0.1, 1000)
  camera.position.set(0, 0, 8.5)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true })
  renderer.setSize(w, h)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  container.appendChild(renderer.domElement)

  graphGroup = new THREE.Group()
  scene.add(graphGroup)

  // Nodes Definition
  // status: 'root' | 'active' | 'success' | 'pruned'
  const nodesData = [
    { id: 0, pos: new THREE.Vector3(0, 0, 0), status: 'root', label: 'Origin' },
    // Branch A (Dead End / Pruned early)
    { id: 1, pos: new THREE.Vector3(-1.8, 1.2, -0.6), status: 'pruned', label: 'Feat A' },
    { id: 2, pos: new THREE.Vector3(-2.6, 2.0, -1.2), status: 'pruned', label: 'Arch A1' },
    // Branch B (Moderate exploration)
    { id: 3, pos: new THREE.Vector3(-1.5, -1.5, 0.8), status: 'pruned', label: 'Loss B' },
    { id: 4, pos: new THREE.Vector3(-2.8, -1.8, 1.4), status: 'pruned', label: 'LR B2' },
    // Branch C (Winning Trajectory: Deep Feature Interaction + Gate)
    { id: 5, pos: new THREE.Vector3(1.6, 0.8, 0.5), status: 'active', label: 'Cycle 1' },
    { id: 6, pos: new THREE.Vector3(2.4, -0.4, -0.4), status: 'active', label: 'Cycle 2' },
    { id: 7, pos: new THREE.Vector3(3.2, 1.4, 0.2), status: 'success', label: 'Champion' }
  ]

  const edgesData = [
    [0, 1], [1, 2],
    [0, 3], [3, 4],
    [0, 5], [5, 6], [6, 7]
  ]

  // Create Nodes
  const nodeMeshes: THREE.Mesh[] = []
  nodesData.forEach(n => {
    let col = 0x38bdf8
    let r = 0.16
    if (n.status === 'root') { col = 0xffffff; r = 0.24 }
    else if (n.status === 'pruned') { col = 0xef4444; r = 0.12 }
    else if (n.status === 'active') { col = 0x00f0ff; r = 0.18 }
    else if (n.status === 'success') { col = 0x00ff9d; r = 0.26 }

    const geo = new THREE.SphereGeometry(r, 20, 20)
    const mat = new THREE.MeshPhongMaterial({
      color: col,
      emissive: col,
      emissiveIntensity: n.status === 'success' ? 0.6 : 0.3,
      shininess: 80
    })
    const mesh = new THREE.Mesh(geo, mat)
    mesh.position.copy(n.pos)
    graphGroup!.add(mesh)
    nodeMeshes.push(mesh)

    // Glowing halo for success and root
    if (n.status === 'success' || n.status === 'root') {
      const haloGeo = new THREE.RingGeometry(r * 1.5, r * 1.7, 32)
      const haloMat = new THREE.MeshBasicMaterial({ color: col, side: THREE.DoubleSide, transparent: true, opacity: 0.6 })
      const halo = new THREE.Mesh(haloGeo, haloMat)
      halo.position.copy(n.pos)
      graphGroup!.add(halo)
    }
  })

  // Create Edges
  edgesData.forEach(([srcIdx, dstIdx]) => {
    const src = nodesData[srcIdx]
    const dst = nodesData[dstIdx]
    const isSuccessPath = (src.status === 'root' || src.status === 'active' || src.status === 'success') &&
                          (dst.status === 'active' || dst.status === 'success')
    const isPruned = dst.status === 'pruned'

    const col = isSuccessPath ? 0x00f0ff : (isPruned ? 0x7f1d1d : 0x475569)
    const opacity = isSuccessPath ? 0.9 : 0.35

    const points = [src.pos, dst.pos]
    const lineGeo = new THREE.BufferGeometry().setFromPoints(points)
    const lineMat = new THREE.LineBasicMaterial({ color: col, transparent: true, opacity, linewidth: isSuccessPath ? 2 : 1 })
    const line = new THREE.Line(lineGeo, lineMat)
    graphGroup!.add(line)
  })

  // Pulsating signal particle travelling along winning path
  const signalGeo = new THREE.SphereGeometry(0.07, 12, 12)
  const signalMat = new THREE.MeshBasicMaterial({ color: 0xffffff })
  const signalMesh = new THREE.Mesh(signalGeo, signalMat)
  graphGroup.add(signalMesh)

  const successPoints = [nodesData[0].pos, nodesData[5].pos, nodesData[6].pos, nodesData[7].pos]
  const successCurve = new THREE.CatmullRomCurve3(successPoints)

  // Floating background ambient dust
  const dustGeo = new THREE.BufferGeometry()
  const dustCount = 80
  const dustPos = new Float32Array(dustCount * 3)
  for (let i = 0; i < dustCount * 3; i += 3) {
    dustPos[i] = (Math.random() - 0.5) * 8
    dustPos[i + 1] = (Math.random() - 0.5) * 6
    dustPos[i + 2] = (Math.random() - 0.5) * 6
  }
  dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPos, 3))
  const dustMat = new THREE.PointsMaterial({ color: 0x64748b, size: 0.03, transparent: true, opacity: 0.5 })
  const dust = new THREE.Points(dustGeo, dustMat)
  graphGroup.add(dust)

  // Lighting
  const amb = new THREE.AmbientLight(0x1e293b, 1.4)
  scene.add(amb)
  const p1 = new THREE.PointLight(0x00f0ff, 2.0, 12)
  p1.position.set(3, 2, 4)
  scene.add(p1)
  const p2 = new THREE.PointLight(0x00ff9d, 2.0, 10)
  p2.position.set(-2, -2, 3)
  scene.add(p2)

  // Synchronous render for PDF export
  renderer.render(scene, camera)

  // Animation Loop
  let clock = 0
  const animate = () => {
    animId = requestAnimationFrame(animate)
    clock += 0.015

    if (!isDragging) {
      targetRotation.y += 0.003
      targetRotation.x = 0.2 + Math.sin(clock * 0.4) * 0.1
    }

    currentRotation.x += (targetRotation.x - currentRotation.x) * 0.08
    currentRotation.y += (targetRotation.y - currentRotation.y) * 0.08

    if (graphGroup) {
      graphGroup.rotation.x = currentRotation.x
      graphGroup.rotation.y = currentRotation.y

      // Signal particle travels along curve
      const t = (clock * 0.35) % 1
      const pointOnCurve = successCurve.getPoint(t)
      signalMesh.position.copy(pointOnCurve)
    }

    if (renderer && scene && camera) {
      renderer.render(scene, camera)
    }
  }
  animate()

  // Pointer interaction
  const handlePointerDown = (e: PointerEvent) => {
    isDragging = true
    prevMousePos = { x: e.clientX, y: e.clientY }
  }

  const handlePointerMove = (e: PointerEvent) => {
    if (!isDragging) return
    const dx = e.clientX - prevMousePos.x
    const dy = e.clientY - prevMousePos.y
    targetRotation.y += dx * 0.007
    targetRotation.x += dy * 0.007
    prevMousePos = { x: e.clientX, y: e.clientY }
  }

  const handlePointerUp = () => {
    isDragging = false
  }

  container.addEventListener('pointerdown', handlePointerDown)
  window.addEventListener('pointermove', handlePointerMove)
  window.addEventListener('pointerup', handlePointerUp)

  const handleResize = () => {
    if (!container || !renderer || !camera) return
    const newW = container.clientWidth || 450
    const newH = container.clientHeight || 340
    camera.aspect = newW / newH
    camera.updateProjectionMatrix()
    renderer.setSize(newW, newH)
  }
  window.addEventListener('resize', handleResize)

  onUnmounted(() => {
    if (animId) cancelAnimationFrame(animId)
    container.removeEventListener('pointerdown', handlePointerDown)
    window.removeEventListener('pointermove', handlePointerMove)
    window.removeEventListener('pointerup', handlePointerUp)
    window.removeEventListener('resize', handleResize)
    if (renderer && renderer.domElement) {
      container.removeChild(renderer.domElement)
      renderer.dispose()
    }
  })
})
</script>

<template>
  <div
    ref="containerRef"
    class="graph-3d-container"
    :style="{ width: props.width, height: props.height }"
  >
    <div class="graph-legend">
      <div class="legend-badge green"><span>●</span> Winning Trajectory (Validated)</div>
      <div class="legend-badge red"><span>×</span> Pruned Hypotheses (Early Stop)</div>
    </div>
  </div>
</template>

<style scoped>
.graph-3d-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: grab;
  user-select: none;
  touch-action: none;
  width: 100%;
  height: 100%;
  min-height: 340px;
}
.graph-3d-container:active {
  cursor: grabbing;
}
.graph-legend {
  position: absolute;
  bottom: 12px;
  right: 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  pointer-events: none;
}
.legend-badge {
  font-family: 'Fira Code', monospace;
  font-size: 11px;
  font-weight: 600;
  padding: 4px 9px;
  border-radius: 4px;
  backdrop-filter: blur(8px);
}
.legend-badge.green {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.4);
  color: #6ee7b7;
}
.legend-badge.red {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #fca5a5;
}
</style>
