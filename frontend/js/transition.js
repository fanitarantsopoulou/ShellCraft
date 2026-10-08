/**
 * Zone transition: a stepped, pixel-style "iris" wipe in the colour of the section you are
 * entering, with its icon and name — like walking into a new area in a retro RPG.
 */

const DURATION = 280; // ms for each half (close / open)
const HOLD = 220; // ms the zone card stays on screen

let overlay;

function ensureOverlay() {
  if (overlay) return overlay;
  overlay = document.createElement("div");
  overlay.className = "warp";
  overlay.setAttribute("aria-hidden", "true");
  document.body.append(overlay);
  return overlay;
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function prefersReducedMotion() {
  return window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;
}

/** Cover the screen, run `swap` (which replaces the page), then reveal the new zone. */
export async function zoneTransition({ color, icon, label }, swap) {
  if (prefersReducedMotion()) {
    swap();
    return;
  }
  const el = ensureOverlay();
  el.style.setProperty("--warp-color", color);
  el.replaceChildren();
  const card = document.createElement("div");
  card.className = "warp-card";
  if (icon) card.append(icon);
  const name = document.createElement("div");
  name.className = "warp-label";
  name.textContent = label;
  card.append(name);
  el.append(card);

  el.className = "warp closing";
  await sleep(DURATION);
  swap();
  await sleep(HOLD);
  el.className = "warp opening";
  await sleep(DURATION);
  el.className = "warp";
}

/** A short entrance for content within the same zone. */
export function pageEnter(node) {
  if (prefersReducedMotion()) return;
  node.classList.remove("page-enter");
  void node.offsetWidth; // restart the animation
  node.classList.add("page-enter");
}
