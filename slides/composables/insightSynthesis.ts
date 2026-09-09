import { reactive } from 'vue'

export const insightDefinitions = [
  { id: 'tools', label: 'Adaptive tools', color: '#e98238', target: '.runtime-band', destination: 'Harness + runtime' },
  { id: 'reasoning', label: 'Fresh reasoning', color: '#38bdf8', target: '.arch-scientist', destination: 'Fresh Scientist' },
  { id: 'audit', label: 'Audited evidence', color: '#a66cff', target: '.arch-meta', destination: 'META Review' },
  { id: 'context', label: 'Reusable context', color: '#ff5c78', target: '.arch-world', destination: 'Research World' },
] as const

export const insightSynthesis = reactive({
  learned: { workflow: false, single: false, tree: false },
  origins: [] as Array<{ x: number; y: number; width: number; height: number }>,
  triggeredByBuild: false,
})
