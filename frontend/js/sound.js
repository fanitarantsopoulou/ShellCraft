/** 8-bit sound effects synthesized with WebAudio — no audio files. */

const KEY = "sudolearn.sound.v1";
const LEGACY_KEY = "linux-learning.sound.v1";
let ctx = null;
let muted = (() => {
  try {
    return (localStorage.getItem(KEY) ?? localStorage.getItem(LEGACY_KEY)) === "off";
  } catch {
    return false;
  }
})();

function audio() {
  // Created lazily inside a user gesture, as browsers require.
  ctx ??= new (window.AudioContext || window.webkitAudioContext)();
  if (ctx.state === "suspended") ctx.resume();
  return ctx;
}

/** Play a sequence of [frequencyHz, durationMs] notes on a chip-style oscillator. */
function play(notes, { type = "square", volume = 0.07, slideTo = null } = {}) {
  if (muted) return;
  const ac = audio();
  let t = ac.currentTime + 0.01;
  for (const [freq, ms] of notes) {
    const osc = ac.createOscillator();
    const gain = ac.createGain();
    const dur = ms / 1000;
    osc.type = type;
    osc.frequency.setValueAtTime(freq, t);
    if (slideTo) osc.frequency.linearRampToValueAtTime(slideTo, t + dur);
    gain.gain.setValueAtTime(volume, t);
    gain.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    osc.connect(gain).connect(ac.destination);
    osc.start(t);
    osc.stop(t + dur + 0.02);
    t += dur;
  }
}

export const sfx = {
  click: () => play([[660, 35]], { volume: 0.04 }),
  select: () => play([[880, 30], [1320, 30]], { volume: 0.04 }),
  next: () => play([[523, 60], [784, 90]]),
  start: () => play([[392, 70], [523, 70], [659, 120]]),
  hint: () => play([[988, 60], [740, 90]], { type: "triangle", volume: 0.09 }),
  correct: () => play([[523, 70], [659, 70], [784, 70], [1047, 160]]),
  wrong: () => play([[196, 260]], { slideTo: 110, volume: 0.06 }),
  invalid: () => play([[330, 80], [330, 80]], { type: "triangle", volume: 0.08 }),
  complete: () => play([[392, 110], [523, 110], [659, 110], [784, 220], [659, 110], [784, 380]]),
};

export function isMuted() {
  return muted;
}

export function setMuted(value) {
  muted = value;
  try {
    localStorage.setItem(KEY, muted ? "off" : "on");
  } catch {
    /* not remembered */
  }
}
