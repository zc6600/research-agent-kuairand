import { useSlideContext } from '@slidev/client'
import { onUnmounted, watch } from 'vue'

// Use the native click cursor so presenter previews, history and Previous agree.
// Manual card interactions remain available; the next native step resumes the talk.
export function useTalkSteps(total: number, apply: (step: number) => void) {
  const { $clicks, $clicksContext, $renderContext } = useSlideContext()
  const id = Symbol('talk-steps')
  $clicksContext.register(id, { max: total, delta: 0 })
  onUnmounted(() => $clicksContext.unregister(id))
  watch($clicks, step => {
    if ($renderContext.value === 'slide' || $renderContext.value === 'presenter')
      apply(Math.min(total, step))
  }, { immediate: true })
  return $clicks
}
