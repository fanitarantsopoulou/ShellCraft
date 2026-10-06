/** Progress lives in this browser only (no accounts yet). */
const KEY = "linux-learning.progress.v1";

function load() {
  try {
    return new Set(JSON.parse(localStorage.getItem(KEY) || "[]"));
  } catch {
    return new Set();
  }
}

const solved = load();

export function isSolved(exerciseId) {
  return solved.has(exerciseId);
}

export function markSolved(exerciseId) {
  solved.add(exerciseId);
  try {
    localStorage.setItem(KEY, JSON.stringify([...solved]));
  } catch {
    /* storage unavailable: progress just isn't remembered */
  }
  document.dispatchEvent(new CustomEvent("progress"));
}

export function solvedCount() {
  return solved.size;
}

/* Best quiz scores, as { quizId: { points, total } }. */
const BEST_KEY = "linux-learning.best.v1";

function loadBest() {
  try {
    return JSON.parse(localStorage.getItem(BEST_KEY) || "{}");
  } catch {
    return {};
  }
}

const best = loadBest();

export function bestScore(quizId) {
  return best[quizId] ?? null;
}

export function recordScore(quizId, points, total) {
  const prev = best[quizId];
  if (prev && prev.points >= points) return false;
  best[quizId] = { points, total };
  try {
    localStorage.setItem(BEST_KEY, JSON.stringify(best));
  } catch {
    /* not remembered */
  }
  return true;
}

export function starsFor(points, total) {
  const ratio = total ? points / total : 0;
  return ratio >= 0.9 ? 3 : ratio >= 0.6 ? 2 : ratio > 0 ? 1 : 0;
}
