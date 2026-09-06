import {Easing, interpolate} from 'remotion';

export const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
export const ease = Easing.bezier(0.22, 1, 0.36, 1);
export const progress = (frame: number, start: number, end: number) =>
  interpolate(frame, [start, end], [0, 1], {...clamp, easing: ease});
export const linear = (frame: number, start: number, end: number) =>
  interpolate(frame, [start, end], [0, 1], clamp);
export const visible = (frame: number, start: number, end: number, fade = 18) =>
  linear(frame, start, start + fade) * (1 - linear(frame, end - fade, end));
export const travel = (frame: number, points: number[], values: number[]) =>
  interpolate(frame, points, values, {...clamp, easing: ease});

export const ink = '#111217';
export const blue = '#1476b5';
export const sky = '#38bdf8';

export const narration = [
  {from: 0, to: 150, text: 'Your research. Your rhythm.'},
  {from: 150, to: 290, text: 'Start with one step.'},
  {from: 290, to: 450, text: 'A fresh scientist explores. The next move is yours.'},
  {from: 450, to: 590, text: 'Or give it room to run.'},
  {from: 590, to: 750, text: 'Set a cycle budget, and let the research continue.'},
  {from: 750, to: 890, text: 'Explore several directions at once.'},
  {from: 890, to: 1050, text: 'Independent worktrees. A reviewer compares the evidence.'},
  {from: 1050, to: 1210, text: 'See what the work actually produced.'},
  {from: 1210, to: 1380, text: 'The state. The result. The evidence behind it.'},
  {from: 1380, to: 1510, text: 'When you want to choose, take the lead.'},
  {from: 1510, to: 1650, text: 'Inspect the review. Explicitly adopt a branch.'},
  {from: 1650, to: 1780, text: 'Bring the research skill into your coding agent.'},
  {from: 1780, to: 1920, text: 'The same world, in your own workflow.'},
  {from: 1920, to: 2070, text: 'Let it run. Make it yours.'},
  {from: 2070, to: 2160, text: 'SciOdyssey.'},
];
