import {Easing, interpolate, spring} from 'remotion';

export const V2C = {
  black: '#06080d',
  blackSoft: '#0e121a',
  white: '#fbfcfb',
  paper: '#f5f7f6',
  ink: '#111217',
  body: '#4b4f58',
  muted: '#8b9099',
  line: '#dfe3e7',
  blue: '#2eb7f4',
  cyan: '#66e4ff',
  deepBlue: '#0877bb',
  violet: '#a36cff',
  orange: '#ff8750',
  rose: '#ff5e7a',
  green: '#25b875',
  gold: '#f0b45f',
} as const;

export const clamp = {
  extrapolateLeft: 'clamp' as const,
  extrapolateRight: 'clamp' as const,
};

const ease = Easing.bezier(0.16, 1, 0.3, 1);

export function p(frame: number, start: number, end: number) {
  return interpolate(frame, [start, end], [0, 1], {...clamp, easing: ease});
}

export function linear(frame: number, start: number, end: number) {
  return interpolate(frame, [start, end], [0, 1], clamp);
}

export function fadeInOut(frame: number, start: number, end: number, fade = 18) {
  return p(frame, start, start + fade) * (1 - p(frame, end - fade, end));
}

export function springIn(frame: number, start: number, from = 0.82) {
  const value = spring({
    frame: frame - start,
    fps: 30,
    config: {damping: 20, stiffness: 110, mass: 0.8},
  });
  return {
    opacity: p(frame, start, start + 14),
    scale: from + value * (1 - from),
  };
}

export function slideIn(frame: number, start: number, distance = 80) {
  const value = p(frame, start, start + 24);
  return {
    opacity: value,
    translate: `${(1 - value) * distance}px 0px`,
  };
}

export function slideUp(frame: number, start: number, distance = 40) {
  const value = p(frame, start, start + 24);
  return {
    opacity: value,
    translate: `0px ${(1 - value) * distance}px`,
  };
}

export function draw(frame: number, start: number, duration = 60) {
  return linear(frame, start, start + duration);
}

export function pulse(frame: number, origin = 0, period = 30, amount = 0.025) {
  return 1 + Math.sin((frame - origin) / period) * amount;
}

export function beat(frame: number, at: number, duration = 12) {
  const attack = p(frame, at - 4, at);
  const release = 1 - p(frame, at, at + duration);
  return attack * release;
}

export function camera(frame: number, points: number[], values: number[]) {
  return interpolate(frame, points, values, {...clamp, easing: ease});
}

export function charReveal(frame: number, start: number, duration: number, text: string) {
  return Math.floor(linear(frame, start, start + duration) * text.length);
}
