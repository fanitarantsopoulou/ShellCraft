import { h, rich } from "./dom.js";

const PRIMARY_TITLES = {
  correct_answer: "Σωστή απάντηση",
  why: "Γιατί;",
  mistake: "Τι πήγε στραβά",
  note: "Σημείωση",
  option: "Η επιλογή σου",
};

const MORE_TITLES = {
  syntax: "Σύνταξη",
  breakdown: "Ανάλυση",
  common_mistake: "Συνηθισμένο λάθος",
  related: "Σχετικές εντολές",
  source: "Πηγή",
};

function codeBlock(lines) {
  return lines?.length ? h("pre", { class: "terminal" }, lines.join("\n")) : null;
}

function block(item, title) {
  switch (item.kind) {
    case "related":
      return h("div", { class: "fb-block" }, h("h4", {}, title),
        h("div", { class: "chips" }, item.code.map((c) => h("code", {}, c))));
    case "breakdown":
      return h("div", { class: "fb-block" }, h("h4", {}, title), codeBlock(item.code),
        h("table", { class: "fb-pairs" },
          item.pairs.map(([token, meaning]) => h("tr", {}, h("td", {}, token), h("td", {}, "→ ", meaning)))));
    case "source":
      return h("div", { class: "fb-block" }, h("h4", {}, title),
        h("a", { href: item.url, target: "_blank", rel: "noopener noreferrer" }, item.text || item.url));
    default:
      return h("div", { class: "fb-block" }, h("h4", {}, title),
        item.text ? h("p", {}, rich(item.text)) : null, codeBlock(item.code));
  }
}

export function renderFeedback(result) {
  const verdict = result.feedback.find((f) => f.kind === "verdict");
  const primary = result.feedback.filter((f) => f.kind in PRIMARY_TITLES);
  const more = result.feedback.filter((f) => f.kind in MORE_TITLES);

  return h("div", { class: "feedback", role: "status" },
    verdict ? h("div", { class: `verdict ${result.outcome}` }, rich(verdict.text)) : null,
    primary.map((f) => block(f, PRIMARY_TITLES[f.kind])),
    more.length
      ? h("details", { class: "more" }, h("summary", {}, "Μάθε περισσότερα για την εντολή"),
          more.map((f) => block(f, MORE_TITLES[f.kind])))
      : null,
  );
}
