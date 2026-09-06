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
let stackGroup: THREE.Group | null = null

let isDragging = false
let prevMousePos = { x: 0, y: 0 }
let targetRotation = { x: 0.55, y: -0.6 }
let currentRotation = { x: 0.55, y: -0.6 }

onMounted(() => {
  if (!containerRef.value) return
  const container = containerRef.value
  const w = container.clientWidth || 450
  const h = container.clientHeight || 350

  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(40, w / h, 0.1, 1000)
  camera.position.set(0, 5.5, 9)
  camera.lookAt(0, 0, 0)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true })
  renderer.setSize(w, h)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  container.appendChild(renderer.domElement)

  stackGroup = new THREE.Group()
  scene.add(stackGroup)

  const plateWidth = 4.8
  const plateDepth = 3.6
  const plateThickness = 0.08

  // Helper to create a floating glowing glass plate
  function createPlate(y: number, colorHex: number, wireColor: number) {
    const group = new THREE.Group()
    group.position.y = y

    const plateGeo = new THREE.BoxGeometry(plateWidth, plateThickness, plateDepth)
    const plateMat = new THREE.MeshPhongMaterial({
      color: colorHex,
      specular: wireColor,
      shininess: 60,
      transparent: true,
      opacity: 0.75
    })
    const plate = new THREE.Mesh(plateGeo, plateMat)
    group.add(plate)

    const wireMat = new THREE.LineBasicMaterial({ color: wireColor, transparent: true, opacity: 0.9 })
    const wire = new THREE.LineSegments(new THREE.EdgesGeometry(plateGeo), wireMat)
    group.add(wire)

    // Corner pillar markers
    const pillarGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.2, 8)
    const pillarMat = new THREE.MeshBasicMaterial({ color: wireColor })
    const offsets = [
      [-plateWidth / 2 + 0.15, -plateDepth / 2 + 0.15],
      [plateWidth / 2 - 0.15, -plateDepth / 2 + 0.15],
      [-plateWidth / 2 + 0.15, plateDepth / 2 - 0.15],
      [plateWidth / 2 - 0.15, plateDepth / 2 - 0.15]
    ]
    offsets.forEach(([ox, oz]) => {
      const p = new THREE.Mesh(pillarGeo, pillarMat)
      p.position.set(ox, 0.1, oz)
      group.add(p)
    })

    return group
  }

  // Tier 1: Research World (Bottom, y = -1.6)
  const tierBottom = createPlate(-1.6, 0x07152b, 0x0284c7)
  // Grid on research world
  const gridHelper = new THREE.GridHelper(3.8, 12, 0x0284c7, 0x0f294d)
  gridHelper.position.y = 0.05
  tierBottom.add(gridHelper)
  stackGroup.add(tierBottom)

  // Tier 2: Pure Evidence Boundary (Middle, y = 0.0)
  const tierMiddle = createPlate(0.0, 0x0c1e3d, 0x00f0ff)
  // Boundary Gatekeeper Crystal
  const gateGeo = new THREE.OctahedronGeometry(0.35, 0)
  const gateMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff, wireframe: true })
  const gateMesh = new THREE.Mesh(gateGeo, gateMat)
  gateMesh.position.y = 0.35
  tierMiddle.add(gateMesh)
  stackGroup.add(tierMiddle)

  // Tier 3: Scientist Fleet (Top, y = 1.6)
  const tierTop = createPlate(1.6, 0x141b36, 0xa855f7)
  // Floating agent nodes
  const agentNodes: THREE.Mesh[] = []
  const agentPositions = [
    [-1.2, 0.35, -0.6, 0x38bdf8], // Hypothesis Agent
    [0.0, 0.5, 0.4, 0xa855f7],   // Meta Scientist Coordinator
    [1.2, 0.35, -0.6, 0x10b981]   // Code/Execution Agent
  ]
  agentPositions.forEach(([ax, ay, az, col]) => {
    const aGeo = new THREE.DodecahedronGeometry(0.22, 0)
    const aMat = new THREE.MeshPhongMaterial({ color: col as number, emissive: col as number, emissiveIntensity: 0.4 })
    const aMesh = new THREE.Mesh(aGeo, aMat)
    aMesh.position.set(ax as number, ay as number, az as number)
    tierTop.add(aMesh)
    agentNodes.push(aMesh)
  })
  stackGroup.add(tierTop)

  // Vertical Data Pillars (Vertical Laser Connectors)
  const beamMat = new THREE.LineBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.6 })
  const cornerCoords = [
    [-plateWidth / 2 + 0.15, -plateDepth / 2 + 0.15],
    [plateWidth / 2 - 0.15, -plateDepth / 2 + 0.15],
    [-plateWidth / 2 + 0.15, plateDepth / 2 - 0.15],
    [plateWidth / 2 - 0.15, plateDepth / 2 - 0.15]
  ]
  cornerCoords.forEach(([cx, cz]) => {
    const points = [
      new THREE.Vector3(cx, -1.6, cz),
      new THREE.Vector3(cx, 1.6, cz)
    ]
    const lineGeo = new THREE.BufferGeometry().setFromPoints(points)
    const line = new THREE.Line(lineGeo, beamMat)
    stackGroup!.add(line)
  })

  // Pulsating vertical data packets (evidence flowing up/down)
  const packetCount = 14
  const packetGeo = new THREE.SphereGeometry(0.05, 8, 8)
  const packetMat = new THREE.MeshBasicMaterial({ color: 0x00ff9d })
  const packets: { mesh: THREE.Mesh; speed: number; yMin: number; yMax: number }[] = []

  for (let i = 0; i < packetCount; i++) {
    const pMesh = new THREE.Mesh(packetGeo, packetMat)
    const rx = (Math.random() - 0.5) * (plateWidth - 1.2)
    const rz = (Math.random() - 0.5) * (plateDepth - 1.0)
    pMesh.position.set(rx, -1.6 + Math.random() * 3.2, rz)
    stackGroup.add(pMesh)
    packets.push({
      mesh: pMesh,
      speed: 0.02 + Math.random() * 0.03,
      yMin: -1.6,
      yMax: 1.6
    })
  }

  // Lighting
  const dirLight = new THREE.DirectionalLight(0xffffff, 1.3)
  dirLight.position.set(6, 12, 8)
  scene.add(dirLight)

  const cyanLight = new THREE.PointLight(0x00f0ff, 2.0, 10)
  cyanLight.position.set(0, 0.2, 0)
  scene.add(cyanLight)

  const purpleLight = new THREE.PointLight(0xa855f7, 2.0, 8)
  purpleLight.position.set(0, 2.2, 0)
  scene.add(purpleLight)

  const ambLight = new THREE.AmbientLight(0x1e293b, 1.2)
  scene.add(ambLight)

  // Synchronous render for PDF export
  renderer.render(scene, camera)

  // Animation Loop
  let clock = 0
  const animate = () => {
    animId = requestAnimationFrame(animate)
    clock += 0.02

    if (!isDragging) {
      targetRotation.y = -0.6 + Math.sin(clock * 0.3) * 0.22
    }

    currentRotation.x += (targetRotation.x - currentRotation.x) * 0.08
    currentRotation.y += (targetRotation.y - currentRotation.y) * 0.08

    if (stackGroup) {
      stackGroup.rotation.x = currentRotation.x
      stackGroup.rotation.y = currentRotation.y

      // Rotate central gatekeeper
      gateMesh.rotation.y = clock * 0.8
      gateMesh.rotation.x = clock * 0.5

      // Agent floating bob
      agentNodes.forEach((node, idx) => {
        node.position.y = 0.35 + Math.sin(clock * 2 + idx * 1.5) * 0.08
        node.rotation.y += 0.015
      })

      // Update vertical data packets
      packets.forEach(p => {
        p.mesh.position.y += p.speed
        if (p.mesh.position.y > p.yMax) {
          p.mesh.position.y = p.yMin
        }
      })
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
    targetRotation.x = Math.max(0.1, Math.min(1.1, targetRotation.x + dy * 0.007))
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
    const newH = container.clientHeight || 350
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
    class="arch-3d-container"
    :style="{ width: props.width, height: props.height }"
  >
    <div class="arch-3d-labels">
      <div class="layer-pill purple">Tier 3: Fresh Scientist Fleet</div>
      <div class="layer-pill cyan">Tier 2: Pure Evidence Gate</div>
      <div class="layer-pill blue">Tier 1: Persistent Research World</div>
    </div>
  </div>
</template>

<style scoped>
.arch-3d-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: grab;
  user-select: none;
  touch-action: none;
  width: 100%;
  height: 100%;
  min-height: 350px;
}
.arch-3d-container:active {
  cursor: grabbing;
}
.arch-3d-labels {
  position: absolute;
  left: 12px;
  top: 14px;
  display: flex;
  flex-direction: column;
  gap: 7px;
  pointer-events: none;
}
.layer-pill {
  font-family: 'Fira Code', monospace;
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 4px;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}
.layer-pill.purple {
  background: rgba(168, 85, 247, 0.18);
  border: 1px solid rgba(168, 85, 247, 0.5);
  color: #e9d5ff;
}
.layer-pill.cyan {
  background: rgba(0, 240, 255, 0.18);
  border: 1px solid rgba(0, 240, 255, 0.5);
  color: #a5f3fc;
}
.layer-pill.blue {
  background: rgba(2, 132, 199, 0.18);
  border: 1px solid rgba(2, 132, 199, 0.5);
  color: #bae6fd;
}
</style>
