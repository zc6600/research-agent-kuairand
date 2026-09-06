<script setup lang="ts">
import { ref } from 'vue'

const props = withDefaults(defineProps<{
  glowColor?: string
  depth?: number
  borderStyle?: string
}>(), {
  glowColor: '#00f0ff',
  depth: 24,
  borderStyle: 'cyan'
})

const cardRef = ref<HTMLDivElement | null>(null)
const transformStyle = ref('')
const glareStyle = ref('')

const handleMouseMove = (e: MouseEvent) => {
  if (!cardRef.value) return
  const rect = cardRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  const centerX = rect.width / 2
  const centerY = rect.height / 2

  const rotateX = ((y - centerY) / centerY) * -9 // max 9 deg
  const rotateY = ((x - centerX) / centerX) * 9

  transformStyle.value = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) translateZ(${props.depth}px)`
  glareStyle.value = `radial-gradient(circle at ${x}px ${y}px, rgba(255, 255, 255, 0.12), transparent 70%)`
}

const handleMouseLeave = () => {
  transformStyle.value = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px)'
  glareStyle.value = 'none'
}
</script>

<template>
  <div
    ref="cardRef"
    class="card-3d-wrapper"
    :class="props.borderStyle"
    :style="{ transform: transformStyle }"
    @mousemove="handleMouseMove"
    @mouseleave="handleMouseLeave"
  >
    <div class="card-3d-glare" :style="{ background: glareStyle }"></div>
    <div class="card-3d-content">
      <slot></slot>
    </div>
  </div>
</template>

<style scoped>
.card-3d-wrapper {
  position: relative;
  background: rgba(13, 22, 41, 0.75);
  backdrop-filter: blur(14px);
  border-radius: 12px;
  padding: 18px 20px;
  transform-style: preserve-3d;
  transition: transform 0.15s ease-out, box-shadow 0.2s ease;
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.6);
  overflow: hidden;
}

.card-3d-wrapper.cyan {
  border: 1px solid rgba(0, 240, 255, 0.28);
  box-shadow: 0 10px 30px -10px rgba(0, 240, 255, 0.15);
}
.card-3d-wrapper.cyan:hover {
  border-color: rgba(0, 240, 255, 0.6);
  box-shadow: 0 16px 40px -10px rgba(0, 240, 255, 0.3);
}

.card-3d-wrapper.purple {
  border: 1px solid rgba(168, 85, 247, 0.28);
  box-shadow: 0 10px 30px -10px rgba(168, 85, 247, 0.15);
}
.card-3d-wrapper.purple:hover {
  border-color: rgba(168, 85, 247, 0.6);
  box-shadow: 0 16px 40px -10px rgba(168, 85, 247, 0.3);
}

.card-3d-wrapper.green {
  border: 1px solid rgba(16, 185, 129, 0.28);
  box-shadow: 0 10px 30px -10px rgba(16, 185, 129, 0.15);
}
.card-3d-wrapper.green:hover {
  border-color: rgba(16, 185, 129, 0.6);
  box-shadow: 0 16px 40px -10px rgba(16, 185, 129, 0.3);
}

.card-3d-wrapper.amber {
  border: 1px solid rgba(245, 158, 11, 0.28);
  box-shadow: 0 10px 30px -10px rgba(245, 158, 11, 0.15);
}
.card-3d-wrapper.amber:hover {
  border-color: rgba(245, 158, 11, 0.6);
  box-shadow: 0 16px 40px -10px rgba(245, 158, 11, 0.3);
}

.card-3d-glare {
  position: absolute;
  inset: 0;
  pointer-events: none;
  border-radius: inherit;
  z-index: 1;
}

.card-3d-content {
  position: relative;
  z-index: 2;
  transform: translateZ(12px);
  transform-style: preserve-3d;
}
</style>
