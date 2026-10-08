import { api } from "./api.js";
import { h, trustedHtml } from "./dom.js";
import { sprite, worldScene } from "./pixelart.js";
import { bestScore, recordScore, solvedCount, starsFor } from "./progress.js";
import { renderQuestion, TYPE_LABELS } from "./question.js";
import { isMuted, setMuted, sfx } from "./sound.js";
import { pageEnter, zoneTransition } from "./transition.js";

const app = document.getElementById("app");
const LEVELS = { beginner: "Αρχάριο", intermediate: "Μεσαίο", advanced: "Προχωρημένο" };
const TRACK_SPRITES = { linux: "penguin", docker: "container", kubernetes: "wheel", cloud: "cloud" };
// Colour of each zone's transition, matching its biome.
const ZONE_COLORS = { home: "#1b2140", linux: "#2b6e36", docker: "#1f6aa8", kubernetes: "#3a62c4", cloud: "#465a9a" };

/* ---------------------------------------------------------------- shell */

let tracks = [];

function renderTabs(activeTrack) {
  const onHome = activeTrack === null;
  document.getElementById("tabs").replaceChildren(
    h("a", {
      class: `tab home${onHome ? " active" : ""}`,
      href: "#/",
      "aria-current": onHome ? "page" : null,
    }, "Home"),
    ...tracks.map((t) =>
      h("a", {
        class: `tab${t.id === activeTrack ? " active" : ""}${t.available ? "" : " soon"}`,
        href: `#/track/${t.id}`,
        "aria-current": t.id === activeTrack ? "page" : null,
      }, t.title)));
}

function renderHud() {
  document.getElementById("stars").textContent = `★ ${solvedCount()}`;
  const btn = document.getElementById("sound");
  btn.textContent = isMuted() ? "ΗΧΟΣ OFF" : "ΗΧΟΣ ON";
  btn.setAttribute("aria-pressed", String(!isMuted()));
}

document.getElementById("sound").addEventListener("click", () => {
  setMuted(!isMuted());
  renderHud();
  sfx.click();
});

// Any element with data-sfx="<name>" plays that sound when clicked.
document.addEventListener("click", (e) => {
  const el = e.target.closest("[data-sfx]");
  if (el && !el.disabled) sfx[el.dataset.sfx]?.();
});

let currentZone; // "home" or a track id; undefined until the first page is shown
let pending = Promise.resolve(); // serialises transitions when navigating quickly

function zoneInfo(zone) {
  if (zone === "home") return { color: ZONE_COLORS.home, icon: sprite("terminal", "warp-icon"), label: "ShellCraft" };
  const track = tracks.find((t) => t.id === zone);
  return {
    color: ZONE_COLORS[zone] ?? ZONE_COLORS.home,
    icon: sprite(TRACK_SPRITES[zone] ?? "terminal", "warp-icon"),
    label: track?.title ?? zone,
  };
}

function show(activeTrack, ...nodes) {
  const zone = activeTrack ?? "home";
  const swap = () => {
    renderTabs(activeTrack);
    app.replaceChildren(...nodes.flat(Infinity).filter(Boolean));
    app.focus({ preventScroll: true });
    window.scrollTo(0, 0);
    pageEnter(app);
  };
  const entering = currentZone !== undefined && zone !== currentZone;
  currentZone = zone;
  pending = pending.then(() => {
    if (!entering) return swap();
    sfx.warp();
    return zoneTransition(zoneInfo(zone), swap);
  });
  return pending;
}

function starRow(stars, cls = "star-row") {
  return h("div", { class: cls, "aria-label": `${stars} από 3 αστέρια` },
    [0, 1, 2].map((i) => sprite("star", `sprite${i < stars ? "" : " off"}`)));
}

/* ---------------------------------------------------------------- quiz state (per browser tab) */

const runs = new Map(); // quizId -> Map(questionId -> saved answer state)
const quizCache = new Map();

async function loadQuiz(id) {
  if (!quizCache.has(id)) quizCache.set(id, await api.quiz(id));
  return quizCache.get(id);
}

function runFor(quizId) {
  if (!runs.has(quizId)) runs.set(quizId, new Map());
  return runs.get(quizId);
}

function savedFor(run, questionId) {
  if (!run.has(questionId)) run.set(questionId, {});
  return run.get(questionId);
}

function score(quiz, run) {
  let points = 0;
  for (const q of quiz.questions) {
    const r = run.get(q.id)?.result;
    if (r) points += r.outcome === "correct" ? 1 : r.score;
  }
  return Math.round(points * 10) / 10;
}

/* ---------------------------------------------------------------- pages */

function home() {
  document.title = "ShellCraft";
  show(null,
    worldScene(),
    h("section", { class: "intro" },
      h("h1", {}, "Μάθε Linux & Cloud, ένα επίπεδο τη φορά"),
      h("p", {}, "Διάλεξε κόσμο. Λύσε quiz που ξεκινούν από τις πρώτες εντολές και φτάνουν σε πραγματικά προβλήματα — με εξήγηση για κάθε απάντηση.")),
    h("div", { class: "track-grid" }, tracks.map((t) =>
      h("a", { class: `track-card frame${t.available ? "" : " locked"}`, href: `#/track/${t.id}`, "data-sfx": "click" },
        sprite(TRACK_SPRITES[t.id] ?? "terminal"),
        h("h2", {}, t.title),
        h("p", {}, t.summary),
        h("span", { class: "status" }, t.available ? `▶ ${t.quiz_count} quiz` : "🔒 Σύντομα")))),
  );
}

function trackTabs(id, active, hasIntro) {
  return h("nav", { class: "subtabs", "aria-label": "Ενότητες" },
    hasIntro
      ? h("a", { href: `#/track/${id}/intro`, class: active === "intro" ? "active" : "", "data-sfx": "click" }, "Εισαγωγή")
      : null,
    h("a", { href: `#/track/${id}`, class: active === "quiz" ? "active" : "", "data-sfx": "click" }, "Quiz"),
    h("a", { href: `#/track/${id}/theory`, class: active === "theory" ? "active" : "", "data-sfx": "click" }, "Θεωρία"));
}

async function trackPage(id, section) {
  const track = await api.track(id);
  document.title = `${track.title} · ShellCraft`;
  const head = h("div", { class: "track-head" }, sprite(TRACK_SPRITES[id] ?? "terminal"),
    h("div", {}, h("h1", {}, track.title), h("p", { class: "muted" }, track.summary)));

  if (!track.available) {
    show(id, head, h("div", { class: "soon-box frame" },
      sprite("terminal"),
      h("h2", {}, "Έρχεται σύντομα"),
      h("p", { class: "muted" }, "Αυτός ο κόσμος χτίζεται ακόμη. Ξεκίνα από το Linux — θα σου χρειαστεί εδώ."),
      h("a", { class: "btn", href: "#/track/linux", "data-sfx": "next" }, "Πήγαινε στο Linux ▶")));
    return;
  }

  const hasIntro = Boolean(track.intro);

  if (section === "intro" && hasIntro) {
    show(id, head, trackTabs(id, "intro", hasIntro),
      trustedHtml("article", track.intro.body_html, { class: "theory intro" }),
      h("div", { class: "start-box" },
        h("a", { class: "btn gold", href: `#/track/${id}`, "data-sfx": "start" }, "Πάμε στα quiz ▶")),
      h("p", { class: "muted sources" }, "Πηγές: ",
        track.intro.sources.map((s, i) => [i ? " · " : "", h("a", { href: s.url, target: "_blank", rel: "noopener noreferrer" }, s.label)])));
    return;
  }

  if (section === "theory") {
    show(id, head, trackTabs(id, "theory", hasIntro),
      track.modules.length ? track.modules.map((m) =>
        h("section", { class: "module frame" },
          h("h2", {}, m.title),
          h("p", {}, m.summary),
          h("ul", { class: "lesson-list" }, m.lessons.map((l, i) =>
            h("li", {}, h("a", { class: "lesson-link", href: `#/lesson/${l.id}`, "data-sfx": "click" },
              h("span", { class: "badge" }, String(i + 1)),
              h("span", {}, l.title),
              h("span", { class: "meta" }, `~${l.est_minutes}′ ανάγνωση`))))))) : h("p", { class: "muted" }, "Δεν υπάρχει ακόμη θεωρία εδώ."));
    return;
  }

  show(id, head, trackTabs(id, "quiz", hasIntro),
    hasIntro
      ? h("a", { class: "intro-hint", href: `#/track/${id}/intro`, "data-sfx": "click" },
          `📖 Πρώτη φορά εδώ; Διάβασε πρώτα «${track.intro.title}» ▶`)
      : null,
    h("ol", { class: "quiz-path" }, track.quizzes.map((q) => {
      const best = bestScore(q.id);
      const stars = best ? starsFor(best.points, best.total) : 0;
      return h("li", {}, h("a", { class: "quiz-card frame", href: `#/quiz/${q.id}`, "data-sfx": "click" },
        h("span", { class: `quiz-num${stars ? " done" : ""}` }, String(q.number)),
        h("span", { class: "quiz-info" },
          h("span", { class: "quiz-name" }, q.title),
          h("span", { class: "muted" }, q.description),
          h("span", { class: "quiz-meta" }, `${LEVELS[q.level] ?? q.level} · ${q.question_count} ερωτήσεις`)),
        h("span", { class: "quiz-best" },
          starRow(stars, "star-row small"),
          best ? h("span", { class: "muted" }, `καλύτερο: ${best.points}/${best.total}`) : null)));
    })));
}

async function lessonPage(id) {
  const lesson = await api.lesson(id);
  const trackId = lesson.module?.id.split(".")[0] ?? "linux";
  document.title = `${lesson.title} · ShellCraft`;
  show(trackId,
    h("nav", { class: "crumbs" }, h("a", { href: `#/track/${trackId}/theory`, "data-sfx": "click" }, "◀ Θεωρία")),
    h("h1", {}, lesson.title),
    h("div", { class: "objective" }, "🎯 ", lesson.objective),
    trustedHtml("article", lesson.body_html, { class: "theory" }),
    lesson.quizzes.length
      ? h("div", { class: "start-box" }, lesson.quizzes.map((q) =>
          h("a", { class: "btn secondary", href: `#/quiz/${q.id}`, "data-sfx": "click" }, `Εξάσκηση: ${q.title} ▶`)))
      : null,
    h("p", { class: "muted" }, "Πηγές: ",
      lesson.sources.map((s, i) => [i ? ", " : "", h("a", { href: s.url, target: "_blank", rel: "noopener noreferrer" }, s.label)])),
  );
}

function quizCrumbs(quiz) {
  return h("nav", { class: "crumbs" }, h("a", { href: `#/track/${quiz.track}`, "data-sfx": "click" }, "◀ Όλα τα quiz"));
}

async function quizIntro(id) {
  const quiz = await loadQuiz(id);
  const best = bestScore(id);
  document.title = `Quiz ${quiz.number}: ${quiz.title}`;
  show(quiz.track,
    quizCrumbs(quiz),
    h("section", { class: "results frame" },
      h("div", { class: "quiz-num big" }, String(quiz.number)),
      h("h1", {}, quiz.title),
      h("p", {}, quiz.description),
      h("p", { class: "muted" }, `${LEVELS[quiz.level] ?? quiz.level} · ${quiz.questions.length} ερωτήσεις`),
      best ? h("p", { class: "muted" }, `Καλύτερο σκορ: ${best.points}/${best.total}`) : null,
      h("div", { class: "results-actions" },
        h("a", {
          class: "btn gold", href: `#/quiz/${id}/q/1`, "data-sfx": "start",
          onclick: () => runs.delete(id),
        }, "Ξεκίνα ▶")),
      quiz.related_lessons.length
        ? h("p", { class: "muted" }, "Θεωρία: ",
            quiz.related_lessons.map((l, i) => [i ? ", " : "", h("a", { href: `#/lesson/${l.id}`, "data-sfx": "click" }, l.title)]))
        : null),
  );
}

function progressBar(quiz, run, current) {
  return h("nav", { class: "progress", "aria-label": "Πρόοδος quiz" },
    quiz.questions.map((q, i) => h("a", {
      href: `#/quiz/${quiz.id}/q/${i + 1}`,
      class: `${run.get(q.id)?.result?.outcome ?? ""}${i === current ? " current" : ""}`,
      "aria-label": `Ερώτηση ${i + 1}`,
      "data-sfx": "click",
    })));
}

async function questionPage(id, n) {
  const quiz = await loadQuiz(id);
  const total = quiz.questions.length;
  if (n < 1 || n > total) {
    location.hash = `#/quiz/${id}/q/1`;
    return;
  }
  const run = runFor(id);
  const q = quiz.questions[n - 1];
  document.title = `Ερώτηση ${n}/${total} · ${quiz.title}`;

  const scoreEl = h("span", { class: "score" });
  const bar = h("div");
  const back = h("a", {
    class: "btn secondary",
    href: n === 1 ? `#/quiz/${id}` : `#/quiz/${id}/q/${n - 1}`,
    "data-sfx": "next",
  }, "◀ Πίσω");
  const next = h("a", { "data-sfx": "next" });

  function refresh() {
    scoreEl.textContent = `ΣΚΟΡ ${score(quiz, run)}/${total}`;
    bar.replaceChildren(progressBar(quiz, run, n - 1));
    const answered = Boolean(run.get(q.id)?.result);
    const last = n === total;
    next.href = last ? `#/quiz/${id}/results` : `#/quiz/${id}/q/${n + 1}`;
    next.textContent = last ? "Αποτελέσματα ▶" : answered ? "Επόμενο ▶" : "Παράλειψη ▶";
    next.className = answered ? "btn" : "btn secondary";
  }

  const question = renderQuestion(q, savedFor(run, q.id), () => {
    refresh();
    next.focus();
  });

  const shown = show(quiz.track,
    quizCrumbs(quiz),
    h("div", { class: "quiz-top" },
      h("span", { class: "quiz-title" }, `QUIZ ${quiz.number} · ${quiz.title} · ${n}/${total}`),
      scoreEl),
    bar,
    question.node,
    h("div", { class: "quiz-nav" }, back, next),
  );
  refresh();
  shown.then(() => question.focus());
}

async function resultsPage(id) {
  const quiz = await loadQuiz(id);
  const run = runFor(id);
  const total = quiz.questions.length;
  const points = score(quiz, run);
  const stars = starsFor(points, total);
  const newBest = recordScore(id, points, total) && points > 0;
  document.title = `Αποτελέσματα · ${quiz.title}`;

  const messages = ["Πάμε ξανά — η επανάληψη κάνει τον master!", "Καλή αρχή!", "Πολύ καλά!", "Τέλεια! Είσαι έτοιμος για το επόμενο επίπεδο."];

  show(quiz.track,
    quizCrumbs(quiz),
    h("section", { class: "results frame" },
      sprite("trophy", "sprite trophy"),
      h("h1", {}, "Τέλος quiz!"),
      h("div", { class: "big-score" }, `${points}/${total}`),
      starRow(stars),
      h("p", {}, messages[stars]),
      newBest ? h("p", { class: "new-best" }, "★ Νέο καλύτερο σκορ!") : null,
      h("ol", { class: "answer-list" }, quiz.questions.map((q, i) => {
        const outcome = run.get(q.id)?.result?.outcome ?? "skipped";
        const mark = { correct: "✓", partial: "~", incorrect: "✗", skipped: "–" }[outcome];
        return h("li", {},
          h("span", { class: `mark ${outcome}` }, mark),
          h("a", { href: `#/quiz/${id}/q/${i + 1}`, "data-sfx": "click" }, `${i + 1}. ${TYPE_LABELS[q.type]}`));
      })),
      h("div", { class: "results-actions" },
        h("a", {
          class: "btn secondary", href: `#/quiz/${id}/q/1`, "data-sfx": "start",
          onclick: () => runs.delete(id),
        }, "↺ Ξανά"),
        quiz.next_quiz
          ? h("a", { class: "btn gold", href: `#/quiz/${quiz.next_quiz.id}`, "data-sfx": "next" }, `Quiz ${quiz.next_quiz.number} ▶`)
          : h("a", { class: "btn", href: `#/track/${quiz.track}`, "data-sfx": "next" }, "Όλα τα quiz ▶"))),
  );
  if (stars >= 2) sfx.complete();
}

/* ---------------------------------------------------------------- router */

const ROUTES = [
  [/^\/$/, () => home()],
  [/^\/track\/([\w-]+)$/, (m) => trackPage(m[1], "quiz")],
  [/^\/track\/([\w-]+)\/theory$/, (m) => trackPage(m[1], "theory")],
  [/^\/track\/([\w-]+)\/intro$/, (m) => trackPage(m[1], "intro")],
  [/^\/track\/([\w-]+)\/intro$/, (m) => trackPage(m[1], "intro")],
  [/^\/lesson\/([\w.-]+)$/, (m) => lessonPage(m[1])],
  [/^\/quiz\/([\w.-]+)$/, (m) => quizIntro(m[1])],
  [/^\/quiz\/([\w.-]+)\/q\/(\d+)$/, (m) => questionPage(m[1], Number(m[2]))],
  [/^\/quiz\/([\w.-]+)\/results$/, (m) => resultsPage(m[1])],
];

async function route() {
  const path = location.hash.slice(1) || "/";
  try {
    if (!tracks.length) tracks = await api.tracks();
    for (const [pattern, handler] of ROUTES) {
      const match = path.match(pattern);
      if (match) return await handler(match);
    }
    location.hash = "#/";
  } catch (err) {
    show(null, h("p", { class: "error" }, err.message), h("a", { class: "btn", href: "#/" }, "◀ Αρχική"));
  }
}

window.addEventListener("hashchange", route);
document.addEventListener("progress", renderHud);
renderHud();
route();
