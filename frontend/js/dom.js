/** Tiny DOM helpers. Text is always set via textContent, never innerHTML. */

export function h(tag, attrs = {}, ...children) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value === undefined || value === null || value === false) continue;
    if (key === "class") el.className = value;
    else if (key.startsWith("on")) el.addEventListener(key.slice(2), value);
    else if (value === true) el.setAttribute(key, "");
    else el.setAttribute(key, value);
  }
  for (const child of children.flat(Infinity)) {
    if (child === null || child === undefined || child === false) continue;
    el.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return el;
}

/** Render text where `backticks` mark inline code. */
export function rich(text) {
  const frag = document.createDocumentFragment();
  String(text ?? "")
    .split(/(`[^`]+`)/g)
    .forEach((part) => {
      if (part.startsWith("`") && part.endsWith("`") && part.length > 2) {
        frag.append(h("code", { class: "inline-code" }, part.slice(1, -1)));
      } else if (part) {
        frag.append(document.createTextNode(part));
      }
    });
  return frag;
}

/** Insert HTML produced by the server's Markdown renderer (raw HTML in content is escaped there). */
export function trustedHtml(tag, html, attrs = {}) {
  const el = h(tag, attrs);
  el.innerHTML = html;
  return el;
}

export function shuffle(items) {
  const a = [...items];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
