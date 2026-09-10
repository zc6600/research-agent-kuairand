import { useNav } from '@slidev/client'
import { computed, ref } from 'vue'

const exploring = ref(false)
export const lastConclusion = ref<string | null>(null)

export function useConclusionNavigation() {
  const nav = useNav()
  const canReturn = computed(() => exploring.value && !['summary', 'thank-you', 'qa'].includes(nav.currentFrontmatter.value.routeAlias))

  async function openConclusion(card: { id: string; route: string; clicks?: number }) {
    lastConclusion.value = card.id
    exploring.value = true
    await nav.go(card.route, card.clicks ?? 0)
  }

  async function returnToConclusions() {
    await nav.go('summary')
    exploring.value = false
  }

  return { openConclusion, returnToConclusions, canReturn }
}
