/** One quiz question: input widgets for every exercise type, evaluation and feedback. */
import { api } from "./api.js";
import { h, shuffle, trustedHtml } from "./dom.js";
import { renderFeedback } from "./feedback.js";
import { markSolved } from "./progress.js";
import { sfx } from "./sound.js";

export const TYPE_LABELS = {
  multiple_choice: "Ερώτηση",
  command_selection: "Διάλεξε την εντολή",
  fill_in_command: "Συμπλήρωσε την εντολή",
  command_writing: "Γράψε την εντολή",
  output_analysis: "Διάβασε το output",
  ordering: "Βάλε σε σειρά",
};

const KEYS = "ΑΒΓΔΕΖ";
const DIFFICULTY = { 1: ["easy", "●○○"], 2: ["medium", "●●○"], 3: ["hard", "●●●"] };

/* Each builder returns { node, read(), restore(submission), focus(), lock() }. */

function choiceInput(ex, saved) {
  const name = `q-${ex.id}`;
  const mono = ex.type === "command_selection";
  // Remember the shuffled order so Back shows the same layout.
  saved.optionOrder ??= shuffle(ex.options).map((o) => o.id);
  const byId = Object.fromEntries(ex.options.map((o) => [o.id, o]));
  const options = saved.optionOrder.map((id, i) =>
    h("label", { class: `option${mono ? " mono" : ""}`, "data-id": id },
      h("input", { type: ex.multi_select ? "checkbox" : "radio", name, value: id, onchange: () => sfx.select() }),
      h("span", { class: "key" }, KEYS[i]),
      h("span", { class: "text" }, byId[id].text)));
  const node = h("fieldset", { class: "options" }, options);
  return {
    node,
    read: () => {
      const selected = [...node.querySelectorAll("input:checked")].map((i) => i.value);
      return selected.length ? { selected } : null;
    },
    restore: (sub) => node.querySelectorAll("input").forEach((i) => { i.checked = sub.selected.includes(i.value); }),
    focus: () => node.querySelector("input")?.focus(),
  };
}

function outputInput(ex, saved) {
  const choice = choiceInput(ex, saved);
  return {
    ...choice,
    node: h("div", {},
      h("div", { class: "output-label" }, "Εντολή και αποτέλεσμα:"),
      h("pre", { class: "terminal" }, `$ ${ex.command}\n${ex.output}`),
      choice.node),
  };
}

function textField(cls, label, onEnter, placeholder) {
  return h("input", {
    class: `term-input ${cls}`, "aria-label": label, placeholder,
    autocomplete: "off", autocapitalize: "off", spellcheck: "false",
    onkeydown: (e) => { if (e.key === "Enter") onEnter(); },
  });
}

function fillInput(ex, saved, submit) {
  const inputs = [];
  const parts = [];
  ex.template_parts.forEach((part, i) => {
    if (part) parts.push(h("span", {}, part.trim()));
    if (i < ex.template_parts.length - 1) {
      const input = textField("blank", `Κενό ${i + 1}`, submit);
      inputs.push(input);
      parts.push(input);
    }
  });
  return {
    node: h("div", { class: "terminal term-line" }, h("span", { class: "ps1" }, "$"), parts),
    read: () => (inputs.every((i) => i.value.trim()) ? { blanks: inputs.map((i) => i.value) } : null),
    restore: (sub) => inputs.forEach((input, i) => { input.value = sub.blanks[i] ?? ""; }),
    focus: () => inputs[0]?.focus(),
  };
}

function commandInput(ex, saved, submit) {
  const input = textField("wide", "Η εντολή σου", submit, "γράψε εδώ…");
  return {
    node: h("div", { class: "terminal term-line" }, h("span", { class: "ps1" }, "user@debian:~$"), input),
    read: () => (input.value.trim() ? { command: input.value } : null),
    restore: (sub) => { input.value = sub.command; },
    focus: () => input.focus(),
  };
}

function orderingInput(ex, saved) {
  const list = h("ol", { class: "order-list" });
  const byId = Object.fromEntries(ex.steps.map((s) => [s.id, s]));
  let order = saved.stepOrder ?? ex.steps.map((s) => s.id);

  function move(index, delta) {
    const target = index + delta;
    [order[index], order[target]] = [order[target], order[index]];
    saved.stepOrder = [...order];
    sfx.click();
    draw(target, delta);
  }

  function draw(focusIndex, delta) {
    list.replaceChildren(...order.map((id, i) =>
      h("li", { class: "order-item" },
        h("span", { class: "num" }, `${i + 1}.`),
        h("span", { class: "text" }, byId[id].text),
        h("button", { type: "button", class: "secondary", "aria-label": "Μετακίνηση πάνω", disabled: i === 0, onclick: () => move(i, -1) }, "▲"),
        h("button", { type: "button", class: "secondary", "aria-label": "Μετακίνηση κάτω", disabled: i === order.length - 1, onclick: () => move(i, 1) }, "▼"))));
    if (focusIndex !== undefined) {
      const buttons = list.children[focusIndex].querySelectorAll("button");
      (delta < 0 ? buttons[0] : buttons[1])?.focus();
    }
  }

  draw();
  return {
    node: list,
    read: () => ({ order: [...order] }),
    restore: (sub) => { order = [...sub.order]; draw(); },
    focus: () => list.querySelector("button:not([disabled])")?.focus(),
  };
}

const BUILDERS = {
  multiple_choice: choiceInput,
  command_selection: choiceInput,
  output_analysis: outputInput,
  fill_in_command: fillInput,
  command_writing: commandInput,
  ordering: orderingInput,
};

/**
 * Render a question. `saved` is this question's persistent quiz state
 * ({ submission, result, hintsShown, optionOrder, stepOrder }); `onAnswered` fires once graded.
 */
export function renderQuestion(ex, saved, onAnswered) {
  const feedbackSlot = h("div");
  const hintSlot = h("div");
  saved.hintsShown ??= 0;

  const input = BUILDERS[ex.type](ex, saved, () => submit());
  const checkBtn = h("button", { type: "button", onclick: () => submit() }, "Έλεγχος");
  const hintBtn = ex.hints.length
    ? h("button", { type: "button", class: "secondary", onclick: showHint }, "Υπόδειξη")
    : null;

  function drawHints() {
    hintSlot.replaceChildren(...ex.hints.slice(0, saved.hintsShown).map((t) => h("div", { class: "hint" }, "💡 ", t)));
    if (hintBtn) hintBtn.disabled = saved.hintsShown >= ex.hints.length || Boolean(saved.result);
  }

  function showHint() {
    saved.hintsShown++;
    sfx.hint();
    drawHints();
  }

  function lock(result) {
    input.node.querySelectorAll("input, button").forEach((el) => { el.disabled = true; });
    checkBtn.hidden = true;
    if (hintBtn) hintBtn.disabled = true;
    const correct = new Set(result.feedback.filter((f) => f.kind === "correct_answer").flatMap((f) => f.code));
    input.node.querySelectorAll(".option").forEach((label) => {
      const text = label.querySelector(".text").textContent;
      if (correct.has(text)) label.classList.add("is-correct");
      else if (label.querySelector("input").checked) label.classList.add("is-wrong");
    });
  }

  async function submit() {
    if (saved.result) return;
    const submission = input.read();
    if (!submission) {
      sfx.invalid();
      feedbackSlot.replaceChildren(h("p", { class: "muted" }, "Δώσε πρώτα μια απάντηση."));
      return;
    }
    checkBtn.disabled = true;
    try {
      const result = await api.answer(ex.id, submission);
      feedbackSlot.replaceChildren(renderFeedback(result));
      if (result.outcome === "invalid") {
        sfx.invalid();
        return; // not graded: let the learner fix the input
      }
      saved.submission = submission;
      saved.result = result;
      if (result.outcome === "correct") {
        sfx.correct();
        markSolved(ex.id);
      } else {
        sfx.wrong();
      }
      lock(result);
      onAnswered(result);
    } catch (err) {
      feedbackSlot.replaceChildren(h("p", { class: "error" }, err.message));
    } finally {
      checkBtn.disabled = false;
    }
  }

  const node = h("section", { class: "question frame" },
    h("div", { class: "q-head" },
      h("span", { class: "q-label" }, TYPE_LABELS[ex.type] ?? ex.type),
      DIFFICULTY[ex.difficulty]
        ? h("span", { class: `difficulty d${ex.difficulty}`, title: "Δυσκολία" },
            `${DIFFICULTY[ex.difficulty][1]} ${DIFFICULTY[ex.difficulty][0]}`)
        : null),
    trustedHtml("div", ex.prompt_html, { class: "prompt" }),
    input.node,
    hintSlot,
    h("div", { class: "q-actions" }, checkBtn, hintBtn),
    feedbackSlot,
  );

  drawHints();
  if (saved.result) {
    input.restore(saved.submission);
    feedbackSlot.replaceChildren(renderFeedback(saved.result));
    lock(saved.result);
  }
  return { node, focus: () => (saved.result ? null : input.focus()) };
}
