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
let terrainGroup: THREE.Group | null = null

let isDragging = false
let prevMousePos = { x: 0, y: 0 }
let targetRotation = { x: 0.65, y: -0.45 }
let currentRotation = { x: 0.65, y: -0.45 }

onMounted(() => {
  if (!containerRef.value) return
  const container = containerRef.value
  const w = container.clientWidth || 450
  const h = container.clientHeight || 340

  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 1000)
  camera.position.set(0, 4.5, 7.5)
  camera.lookAt(0, 0, 0)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true })
  renderer.setSize(w, h)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  container.appendChild(renderer.domElement)

  terrainGroup = new THREE.Group()
  scene.add(terrainGroup)

  // Parametric Loss Landscape Surface
  const gridX = 40
  const gridY = 40
  const size = 6.0
  const geo = new THREE.PlaneGeometry(size, size, gridX, gridY)
  geo.rotateX(-Math.PI / 2)

  const pos = geo.attributes.position
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i)
    const z = pos.getZ(i)
    // Loss surface equation: two distinct basins with a saddle ridge
    const basin1 = -0.9 * Math.exp(-((x + 1.4) ** 2 + (z + 1.2) ** 2) / 1.6) // Local trap
    const basin2 = -1.6 * Math.exp(-((x - 1.5) ** 2 + (z - 1.2) ** 2) / 2.0) // Global optimum
    const ripple = 0.15 * Math.sin(x * 2.5) * Math.cos(z * 2.5)
    const y = basin1 + basin2 + ripple + 0.35 * Math.sin(Math.sqrt(x * x + z * z) * 1.5)
    pos.setY(i, y)
  }
  geo.computeVertexNormals()

  // Shaded transparent terrain
  const mat = new THREE.MeshPhongMaterial({
    color: 0x0f2744,
    specular: 0x00f0ff,
    shininess: 40,
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.85,
    wireframe: false
  })
  const mesh = new THREE.Mesh(geo, mat)
  terrainGroup.add(mesh)

  // Overlay wireframe contour lines
  const wireMat = new THREE.MeshBasicMaterial({
    color: 0x38bdf8,
    wireframe: true,
    transparent: true,
    opacity: 0.25
  })
  const wireMesh = new THREE.Mesh(geo, wireMat)
  wireMesh.position.y += 0.005
  terrainGroup.add(wireMesh)

  // Baseline Stuck Point (Local Minimum)
  const trapGeo = new THREE.SphereGeometry(0.14, 16, 16)
  const trapMat = new THREE.MeshBasicMaterial({ color: 0xef4444 })
  const trapMesh = new THREE.Mesh(trapGeo, trapMat)
  trapMesh.position.set(-1.4, -0.65, -1.2)
  terrainGroup.add(trapMesh)

  // SciOdyssey Global Optimum Point
  const optGeo = new THREE.SphereGeometry(0.18, 16, 16)
  const optMat = new THREE.MeshBasicMaterial({ color: 0x00ff9d })
  const optMesh = new THREE.Mesh(optGeo, optMat)
  optMesh.position.set(1.5, -1.25, 1.2)
  terrainGroup.add(optMesh)

  // Pulsating ring around optimum
  const optRingGeo = new THREE.RingGeometry(0.24, 0.28, 32)
  optRingGeo.rotateX(-Math.PI / 2)
  const optRingMat = new THREE.MeshBasicMaterial({
    color: 0x00ff9d,
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.8
  })
  const optRing = new THREE.Mesh(optRingGeo, optRingMat)
  optRing.position.set(1.5, -1.24, 1.2)
  terrainGroup.add(optRing)

  // Multi-basin Leaping Trajectory Curve (SciOdyssey exploration path)
  const curvePoints = [
    new THREE.Vector3(-1.4, -0.65, -1.2), // Starts near baseline
    new THREE.Vector3(-0.6, 0.3, -0.4),   // Leap 1 over saddle
    new THREE.Vector3(0.2, -0.2, 0.1),    // Explorer branch point
    new THREE.Vector3(0.7, 0.5, 0.6),     // Leap 2 exploratory ridge
    new THREE.Vector3(1.5, -1.25, 1.2)    // Global optimum reached
  ]
  const curve = new THREE.CatmullRomCurve3(curvePoints)
  const tubeGeo = new THREE.TubeGeometry(curve, 40, 0.035, 8, false)
  const tubeMat = new THREE.MeshBasicMaterial({
    color: 0x00f0ff,
    transparent: true,
    opacity: 0.95
  })
  const trajectoryMesh = new THREE.Mesh(tubeGeo, tubeMat)
  terrainGroup.add(trajectoryMesh)

  // Lighting
  const dirLight = new THREE.DirectionalLight(0xffffff, 1.2)
  dirLight.position.set(5, 10, 7)
  scene.add(dirLight)

  const cyanLight = new THREE.PointLight(0x00f0ff, 2.5, 10)
  cyanLight.position.set(1.5, 2, 1.2)
  scene.add(cyanLight)

  const redLight = new THREE.PointLight(0xef4444, 1.5, 8)
  redLight.position.set(-1.4, 1.5, -1.2)
  scene.add(redLight)

  const ambLight = new THREE.AmbientLight(0x1e293b, 1.0)
  scene.add(ambLight)

  // Synchronous render for PDF export
  renderer.render(scene, camera)

  // Animation
  let clock = 0
  const animate = () => {
    animId = requestAnimationFrame(animate)
    clock += 0.02

    if (!isDragging) {
      targetRotation.y = -0.45 + Math.sin(clock * 0.4) * 0.2
    }

    currentRotation.x += (targetRotation.x - currentRotation.x) * 0.08
    currentRotation.y += (targetRotation.y - currentRotation.y) * 0.08

    if (terrainGroup) {
      terrainGroup.rotation.x = currentRotation.x
      terrainGroup.rotation.y = currentRotation.y

      const s = 1.0 + Math.sin(clock * 3) * 0.18
      optRing.scale.set(s, s, s)
      optRingMat.opacity = 0.4 + Math.cos(clock * 3) * 0.4
    }

    if (renderer && scene && camera) {
      renderer.render(scene, camera)
    }
  }
  animate()

  // Pointer Interaction
  const handlePointerDown = (e: PointerEvent) => {
    isDragging = true
    prevMousePos = { x: e.clientX, y: e.clientY }
  }

  const handlePointerMove = (e: PointerEvent) => {
    if (!isDragging) return
    const dx = e.clientX - prevMousePos.x
    const dy = e.clientY - prevMousePos.y
    targetRotation.y += dx * 0.007
    targetRotation.x = Math.max(0.2, Math.min(1.2, targetRotation.x + dy * 0.007))
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
    class="landscape-3d-container"
    :style="{ width: props.width, height: props.height }"
  >
    <div class="landscape-3d-overlay">
      <div class="badge-tag red"><span>●</span> Baseline Stuck Basin</div>
      <div class="badge-tag green"><span>▲</span> SciOdyssey Global Peak</div>
    </div>
  </div>
</template>

<style scoped>
.landscape-3d-container {
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
.landscape-3d-container:active {
  cursor: grabbing;
}
.landscape-3d-overlay {
  position: absolute;
  top: 8px;
  right: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  pointer-events: none;
}
.badge-tag {
  font-family: 'Fira Code', monospace;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  backdrop-filter: blur(8px);
}
.badge-tag.red {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #fca5a5;
}
.badge-tag.green {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.4);
  color: #6ee7b7;
}
</style>
