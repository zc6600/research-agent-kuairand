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
let chartGroup: THREE.Group | null = null

let isDragging = false
let prevMousePos = { x: 0, y: 0 }
let targetRotation = { x: 0.45, y: -0.4 }
let currentRotation = { x: 0.45, y: -0.4 }

onMounted(() => {
  if (!containerRef.value) return
  const container = containerRef.value
  const w = container.clientWidth || 450
  const h = container.clientHeight || 340

  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(40, w / h, 0.1, 1000)
  camera.position.set(0, 4.2, 7.5)
  camera.lookAt(0, 0, 0)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true })
  renderer.setSize(w, h)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  container.appendChild(renderer.domElement)

  chartGroup = new THREE.Group()
  scene.add(chartGroup)

  // Ground Base Platform
  const baseGeo = new THREE.CylinderGeometry(3.6, 3.8, 0.15, 32)
  const baseMat = new THREE.MeshPhongMaterial({
    color: 0x071120,
    specular: 0x1e293b,
    shininess: 30
  })
  const baseMesh = new THREE.Mesh(baseGeo, baseMat)
  baseMesh.position.y = -0.075
  chartGroup.add(baseMesh)

  const ringGeo = new THREE.RingGeometry(3.4, 3.5, 48)
  ringGeo.rotateX(-Math.PI / 2)
  const ringMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff, side: THREE.DoubleSide, transparent: true, opacity: 0.4 })
  const ring = new THREE.Mesh(ringGeo, ringMat)
  ring.position.y = 0.01
  chartGroup.add(ring)

  // 3 Metric Groups: [AUC, GAUC, Cold-Start GAUC]
  // Pairs: [Baseline (Gray/Blue), SciOdyssey (Neon Cyan/Emerald)]
  const metrics = [
    { label: 'AUC', baseVal: 0.6865, agentVal: 0.7088, xOffset: -2.0 },
    { label: 'GAUC', baseVal: 0.6433, agentVal: 0.6775, xOffset: 0.0 },
    { label: 'Cold-Start', baseVal: 0.5980, agentVal: 0.6315, xOffset: 2.0 }
  ]

  // Height scaler
  const scaleH = (val: number) => (val - 0.5) * 8.5 // 0.6 -> ~0.85, 0.7088 -> ~1.77

  metrics.forEach(m => {
    const baseH = scaleH(m.baseVal)
    const agentH = scaleH(m.agentVal)
    const barW = 0.5
    const barD = 0.5

    // 1. Baseline Bar (Subdued slate navy)
    const bGeo = new THREE.BoxGeometry(barW, baseH, barD)
    const bMat = new THREE.MeshPhongMaterial({
      color: 0x1e293b,
      specular: 0x475569,
      shininess: 40
    })
    const bMesh = new THREE.Mesh(bGeo, bMat)
    bMesh.position.set(m.xOffset - 0.35, baseH / 2, 0)
    chartGroup!.add(bMesh)

    // Baseline Cap
    const bCapGeo = new THREE.PlaneGeometry(barW, barD)
    bCapGeo.rotateX(-Math.PI / 2)
    const bCapMat = new THREE.MeshBasicMaterial({ color: 0x64748b })
    const bCap = new THREE.Mesh(bCapGeo, bCapMat)
    bCap.position.set(m.xOffset - 0.35, baseH + 0.005, 0)
    chartGroup!.add(bCap)

    // 2. SciOdyssey Bar (Luminous Neon Cyan/Mint Prism)
    const aGeo = new THREE.BoxGeometry(barW, agentH, barD)
    const aMat = new THREE.MeshPhongMaterial({
      color: 0x0369a1,
      specular: 0x00f0ff,
      shininess: 90,
      emissive: 0x0284c7,
      emissiveIntensity: 0.25
    })
    const aMesh = new THREE.Mesh(aGeo, aMat)
    aMesh.position.set(m.xOffset + 0.35, agentH / 2, 0)
    chartGroup!.add(aMesh)

    // SciOdyssey Glowing Cap
    const aCapGeo = new THREE.PlaneGeometry(barW, barD)
    aCapGeo.rotateX(-Math.PI / 2)
    const aCapMat = new THREE.MeshBasicMaterial({ color: 0x00ff9d })
    const aCap = new THREE.Mesh(aCapGeo, aCapMat)
    aCap.position.set(m.xOffset + 0.35, agentH + 0.005, 0)
    chartGroup!.add(aCap)

    // Wireframe edges for high-tech prism look
    const edges = new THREE.LineSegments(
      new THREE.EdgesGeometry(aGeo),
      new THREE.LineBasicMaterial({ color: 0x00f0ff, transparent: true, opacity: 0.85 })
    )
    edges.position.copy(aMesh.position)
    chartGroup!.add(edges)
  })

  // Lighting
  const dirLight = new THREE.DirectionalLight(0xffffff, 1.4)
  dirLight.position.set(5, 10, 7)
  scene.add(dirLight)

  const cyanLight = new THREE.PointLight(0x00f0ff, 2.2, 10)
  cyanLight.position.set(0, 3, 2)
  scene.add(cyanLight)

  const emeraldLight = new THREE.PointLight(0x00ff9d, 1.8, 8)
  emeraldLight.position.set(2, 2.5, 1)
  scene.add(emeraldLight)

  const ambLight = new THREE.AmbientLight(0x1e293b, 1.2)
  scene.add(ambLight)

  // Immediate render for PDF export
  renderer.render(scene, camera)

  // Animation Loop
  let clock = 0
  const animate = () => {
    animId = requestAnimationFrame(animate)
    clock += 0.02

    if (!isDragging) {
      targetRotation.y = -0.4 + Math.sin(clock * 0.35) * 0.2
    }

    currentRotation.x += (targetRotation.x - currentRotation.x) * 0.08
    currentRotation.y += (targetRotation.y - currentRotation.y) * 0.08

    if (chartGroup) {
      chartGroup.rotation.x = currentRotation.x
      chartGroup.rotation.y = currentRotation.y
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
    targetRotation.x = Math.max(0.1, Math.min(0.9, targetRotation.x + dy * 0.007))
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
    class="prism-chart-container"
    :style="{ width: props.width, height: props.height }"
  >
    <div class="chart-legend">
      <div class="legend-item"><span class="swatch baseline"></span> Baseline</div>
      <div class="legend-item"><span class="swatch agent"></span> SciOdyssey (+5.6% Cold-Start)</div>
    </div>
  </div>
</template>

<style scoped>
.prism-chart-container {
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
.prism-chart-container:active {
  cursor: grabbing;
}
.chart-legend {
  position: absolute;
  top: 10px;
  right: 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  pointer-events: none;
}
.legend-item {
  font-family: 'Fira Code', monospace;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(15, 23, 42, 0.7);
  padding: 4px 10px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(8px);
  color: #e2e8f0;
}
.swatch {
  width: 10px;
  height: 10px;
  border-radius: 2px;
}
.swatch.baseline {
  background: #64748b;
}
.swatch.agent {
  background: #00ff9d;
  box-shadow: 0 0 8px #00ff9d;
}
</style>
