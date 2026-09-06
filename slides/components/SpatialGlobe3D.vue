<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'

const props = withDefaults(defineProps<{
  width?: string
  height?: string
  autoRotate?: boolean
}>(), {
  width: '100%',
  height: '100%',
  autoRotate: true
})

const containerRef = ref<HTMLDivElement | null>(null)
let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let renderer: THREE.WebGLRenderer | null = null
let animId: number | null = null
let globeGroup: THREE.Group | null = null

// Interaction state
let isDragging = false
let prevMousePos = { x: 0, y: 0 }
let targetRotation = { x: 0.2, y: 0.4 }
let currentRotation = { x: 0.2, y: 0.4 }

onMounted(() => {
  if (!containerRef.value) return
  const container = containerRef.value
  const w = container.clientWidth || 400
  const h = container.clientHeight || 400

  // 1. Scene & Camera
  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 1000)
  camera.position.z = 5.8

  // 2. Renderer
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true })
  renderer.setSize(w, h)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  container.appendChild(renderer.domElement)

  // 3. Globe Group
  globeGroup = new THREE.Group()
  scene.add(globeGroup)

  // Central Geodesic Sphere
  const sphereGeo = new THREE.IcosahedronGeometry(1.6, 2)
  const sphereMat = new THREE.MeshBasicMaterial({
    color: 0x00f0ff,
    wireframe: true,
    transparent: true,
    opacity: 0.35
  })
  const sphereMesh = new THREE.Mesh(sphereGeo, sphereMat)
  globeGroup.add(sphereMesh)

  // Inner Solid Glow Sphere
  const innerGeo = new THREE.SphereGeometry(1.35, 32, 32)
  const innerMat = new THREE.MeshBasicMaterial({
    color: 0x07152d,
    transparent: true,
    opacity: 0.75
  })
  const innerMesh = new THREE.Mesh(innerGeo, innerMat)
  globeGroup.add(innerMesh)

  // Outer Point Cloud (Research Coordinates)
  const pointsGeo = new THREE.IcosahedronGeometry(1.62, 3)
  const pointCount = pointsGeo.attributes.position.count
  const pointsMat = new THREE.PointsMaterial({
    color: 0x38bdf8,
    size: 0.045,
    transparent: true,
    opacity: 0.9
  })
  const points = new THREE.Points(pointsGeo, pointsMat)
  globeGroup.add(points)

  // Orbital Rings
  const ring1Geo = new THREE.RingGeometry(2.1, 2.13, 64)
  const ring1Mat = new THREE.MeshBasicMaterial({
    color: 0x6366f1,
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.6
  })
  const ring1 = new THREE.Mesh(ring1Geo, ring1Mat)
  ring1.rotation.x = Math.PI / 3
  ring1.rotation.y = Math.PI / 6
  globeGroup.add(ring1)

  const ring2Geo = new THREE.RingGeometry(2.4, 2.43, 64)
  const ring2Mat = new THREE.MeshBasicMaterial({
    color: 0x00ff9d,
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.5
  })
  const ring2 = new THREE.Mesh(ring2Geo, ring2Mat)
  ring2.rotation.x = -Math.PI / 4
  ring2.rotation.z = Math.PI / 5
  globeGroup.add(ring2)

  // Orbiting Data Beacons (Satellites)
  const beaconGeo = new THREE.SphereGeometry(0.08, 16, 16)
  const beacon1Mat = new THREE.MeshBasicMaterial({ color: 0x00f0ff })
  const beacon1 = new THREE.Mesh(beaconGeo, beacon1Mat)
  const beacon2Mat = new THREE.MeshBasicMaterial({ color: 0xf59e0b })
  const beacon2 = new THREE.Mesh(beaconGeo, beacon2Mat)
  const beacon3Mat = new THREE.MeshBasicMaterial({ color: 0xa855f7 })
  const beacon3 = new THREE.Mesh(beaconGeo, beacon3Mat)
  globeGroup.add(beacon1, beacon2, beacon3)

  // Starfield Particles
  const starsGeo = new THREE.BufferGeometry()
  const starCount = 120
  const starPositions = new Float32Array(starCount * 3)
  for (let i = 0; i < starCount * 3; i += 3) {
    const radius = 2.8 + Math.random() * 2.5
    const theta = Math.random() * Math.PI * 2
    const phi = Math.acos(Math.random() * 2 - 1)
    starPositions[i] = radius * Math.sin(phi) * Math.cos(theta)
    starPositions[i + 1] = radius * Math.sin(phi) * Math.sin(theta)
    starPositions[i + 2] = radius * Math.cos(phi)
  }
  starsGeo.setAttribute('position', new THREE.BufferAttribute(starPositions, 3))
  const starsMat = new THREE.PointsMaterial({
    color: 0x94a3b8,
    size: 0.03,
    transparent: true,
    opacity: 0.7
  })
  const starField = new THREE.Points(starsGeo, starsMat)
  globeGroup.add(starField)

  // Synchronous Initial Render (ensures Playwright takes screenshot with rendered WebGL)
  renderer.render(scene, camera)

  // Animation Loop
  let clock = 0
  const animate = () => {
    animId = requestAnimationFrame(animate)
    clock += 0.015

    if (props.autoRotate && !isDragging) {
      targetRotation.y += 0.004
      targetRotation.x = Math.sin(clock * 0.3) * 0.15
    }

    // Smooth inertia interpolation
    currentRotation.x += (targetRotation.x - currentRotation.x) * 0.08
    currentRotation.y += (targetRotation.y - currentRotation.y) * 0.08

    if (globeGroup) {
      globeGroup.rotation.x = currentRotation.x
      globeGroup.rotation.y = currentRotation.y

      // Orbiting satellites animation
      const r1 = 2.115
      const angle1 = clock * 0.8
      beacon1.position.set(
        Math.cos(angle1) * r1 * Math.cos(Math.PI / 6),
        Math.sin(angle1) * r1 * Math.cos(Math.PI / 3),
        Math.sin(angle1) * r1 * Math.sin(Math.PI / 3)
      )

      const r2 = 2.415
      const angle2 = -clock * 0.6
      beacon2.position.set(
        Math.cos(angle2) * r2 * Math.cos(Math.PI / 5),
        Math.sin(angle2) * r2 * Math.sin(Math.PI / 5),
        Math.cos(angle2) * r2 * Math.sin(-Math.PI / 4)
      )

      beacon3.position.set(
        Math.sin(clock * 0.5) * 1.8,
        Math.cos(clock * 0.7) * 1.8,
        Math.sin(clock * 0.3) * 1.8
      )
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
    targetRotation.y += dx * 0.008
    targetRotation.x += dy * 0.008
    prevMousePos = { x: e.clientX, y: e.clientY }
  }

  const handlePointerUp = () => {
    isDragging = false
  }

  container.addEventListener('pointerdown', handlePointerDown)
  window.addEventListener('pointermove', handlePointerMove)
  window.addEventListener('pointerup', handlePointerUp)

  // Handle Resize
  const handleResize = () => {
    if (!container || !renderer || !camera) return
    const newW = container.clientWidth || 400
    const newH = container.clientHeight || 400
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
    class="spatial-globe-container"
    :style="{ width: props.width, height: props.height }"
  ></div>
</template>

<style scoped>
.spatial-globe-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: grab;
  user-select: none;
  touch-action: none;
  width: 100%;
  height: 100%;
  min-height: 360px;
}
.spatial-globe-container:active {
  cursor: grabbing;
}
</style>
