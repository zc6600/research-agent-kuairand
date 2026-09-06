import {Easing, interpolate, spring} from 'remotion';

export const COLORS = {
  ink: '#111217',
  body: '#33343a',
  muted: '#7d7d82',
  line: '#e6e6e8',
  paper: '#fbfcfb',
  blue: '#38bdf8',
  blueDeep: '#1476b5',
  orange: '#ff873f',
  rose: '#ff5c78',
  purple: '#a66cff',
  green: '#16803b',
  aqua: '#20d9a0',
  navy: '#25324d',
} as const;

export const clamp = {
  extrapolateLeft: 'clamp' as const,
  extrapolateRight: 'clamp' as const,
};

const ease = Easing.bezier(0.22, 1, 0.36, 1);

export function progress(frame: number, start: number, end: number) {
  return interpolate(frame, [start, end], [0, 1], {...clamp, easing: ease});
}
export function linear(frame: number, start: number, end: number) {
  return interpolate(frame, [start, end], [0, 1], clamp);
}

export function reveal(frame: number, start = 0, duration = 24, distance = 24) {
  const p = progress(frame, start, start + duration);
  return {
    opacity: p,
    transform: `translate3d(0, ${(1 - p) * distance}px, 0)`,
  };
}

export function revealX(frame: number, start = 0, duration = 24, distance = 28) {
  const p = progress(frame, start, start + duration);
  return {
    opacity: p,
    transform: `translate3d(${(1 - p) * distance}px, 0, 0)`,
  };
}

export function scaleIn(frame: number, start = 0, from = 0.88) {
  const springValue = spring({
    frame: frame - start,
    fps: 30,
    config: {damping: 18, stiffness: 100, mass: 0.8},
  });
  return {
    opacity: linear(frame, start, start + 12),
    transform: `scale(${from + springValue * (1 - from)})`,
  };
}

export function fadeOut(frame: number, start: number, end: number) {
  return 1 - progress(frame, start, end);
}

export function visible(frame: number, start: number, end: number, fade = 24) {
  return progress(frame, start, start + fade) * fadeOut(frame, end - fade, end);
}

export function draw(frame: number, start: number, duration = 72) {
  return progress(frame, start, start + duration);
}

export function camera(frame: number, points: number[], values: number[]) {
  return interpolate(frame, points, values, {...clamp, easing: ease});
}
