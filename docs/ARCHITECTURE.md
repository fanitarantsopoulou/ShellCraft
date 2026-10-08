# ShellCraft — Architecture

This document describes how ShellCraft works today. The original, much broader design
proposal (accounts, server-side progress, real terminal sandboxes) is kept in the git history
(commit `c75b4b7`); the parts of it that are not built yet are listed under [Not built yet](#not-built-yet).

## Overview

```
Browser (vanilla JS, no build step)
   │  same origin, http://localhost:8080
   ▼
Caddy ── static files (frontend/) ── strict CSP, no-cache
   │
   └── /api/* ──► FastAPI (backend/)
                    ├── loads content/ (YAML + Markdown) into memory,
                    │   reloads automatically when a file changes
                    ├── serves tracks, intros, lessons and quizzes
                    └── evaluates answers (nothing is ever executed)

PostgreSQL + Alembic are wired up for future accounts and progress, but the app does not use
the database yet. Learner progress (solved questions, best scores, sound setting) lives in the
browser's localStorage.
```

Everything runs with Docker Compose (`deploy/compose.yaml`): `proxy` (Caddy), `api` (FastAPI)
and `db` (PostgreSQL). Only the proxy is published, on `127.0.0.1:8080`.

## Repository layout

| Path | What lives there |
|---|---|
| `content/` | All learning material as YAML/Markdown. No code changes are needed to add questions. |
| `backend/app/content/` | Content schemas (Pydantic), loader, lint, Markdown rendering |
| `backend/app/evaluation/` | Shell parser, command normalizer, evaluators, feedback. No database, no I/O. |
| `backend/app/learning/` | API routes and the learner-facing views of content (answers stripped) |
| `backend/cli/` | `python -m cli.content validate` |
| `backend/tests/` | Unit, API and content tests (pytest) |
| `frontend/` | `index.html`, CSS, ES modules, pixel font |
| `deploy/` | Compose file, Caddyfile, Dockerfile |

## Content model

```
content/
  sources.yaml                      allowlist of official documentation sources
  tracks/<track>/
    track.yaml                      title, biome, skills (a prerequisite graph)
    intro.md                        "what is Linux / Docker / …", with citations
    modules/<module>/
      module.yaml
      lessons/*.md                  theory pages (front matter + Markdown)
    quizzes/NN-<name>.yaml          one quiz per file, questions inline
  commands/<area>/<command>.yaml    command reference: synopsis, options, examples, mistakes
```

- **Tracks** are the top-level sections (Linux, Docker, Kubernetes, Cloud). Each opens on its
  intro, then theory, then quizzes.
- **Quizzes** contain the questions. A question inherits `level` and `skills` from its quiz and
  gets the id `<quiz id>.<question id>`.
- **Question types**: `multiple_choice`, `command_selection`, `fill_in_command`,
  `command_writing`, `output_analysis`, `ordering`. Each type has its own typed `spec`.
- **Wrong options** must explain why they are wrong, and options that are not real commands
  (`copy`, `ren`, `docker ls`) must say so (`existence: nonexistent | not_installed | platform_specific`).
- **Command references** list every option with all its spellings. Option lists were generated
  from `--help` on the target systems; descriptions are written by hand.
- **Citations** point only to registered official sources (kernel.org, GNU, man-pages, Debian,
  Docker, Kubernetes, NIST, AWS, Azure, Google Cloud, …).

## Validation

`make content-validate` (also run by the test suite) fails on any of:

- schema errors (unknown keys, missing explanations, wrong number of correct options, …);
- references to unknown skills, commands, lessons or tracks; prerequisite cycles;
- citations outside a source's allowed domains, or not re-verified for over a year;
- **questions not ordered from easy to hard** (recognize → apply → combine/troubleshoot →
  scenario); the UI shows this as easy / medium / hard;
- `command_writing` test cases: every question declares commands that must be accepted and
  commands that must be rejected, and they are run through the real evaluator.

Command outputs and error messages shown in questions were captured on real systems:
Debian 13.7 (GNU coreutils 9.7), Docker 29.5.2 and Kubernetes v1.37.1.

## Evaluating written commands

Nothing the learner types is executed. A submitted command goes through:

1. **Parsing**: POSIX shell quoting, pipes, `;`/`&&`/`||` and `<`/`>`/`>>`. Expansions
   (`$…`, backticks), subshells, background jobs and fd redirects are rejected as unsupported
   rather than guessed at.
2. **Normalizing**, using only what the command reference declares:
   - command aliases map to one name (`docker ps` = `docker container ls`);
   - option spellings map to one flag (`-R` = `-r` = `--recursive`), bundled flags are split
     (`-rf` = `-r -f`) and option order does not matter;
   - for `docker run`/`exec`, everything after the image is an argument to the container;
   - `./file` = `file`; obsolete `head -3` = `head -n 3` (accepted, with a note);
   - per question, harmless flags can be marked optional (e.g. `cp -v`).
3. **Matching** against the question's accepted answers, then its known mistakes (each with
   targeted feedback). Anything else is wrong, with a diagnosis against the closest accepted
   answer (wrong command, unknown option, argument order, …).

Feedback combines the question's explanation with the command reference (syntax, a worked
example, a common mistake, related commands and the source).

## Frontend

- Vanilla JavaScript ES modules, no framework and no build step.
- Hash routes: `#/`, `#/track/<id>` (intro), `#/track/<id>/theory`, `#/track/<id>/quiz`,
  `#/quiz/<id>/q/<n>`, `#/quiz/<id>/results`, `#/lesson/<id>`.
- Pixel art is drawn as SVG from small character maps; sounds are synthesized with WebAudio.
  Moving between sections plays a short pixel "iris" transition.
- Greek text uses the system font; the pixel font (Press Start 2P, SIL OFL 1.1) is limited to
  Latin characters so Greek stays readable.
- Respects `prefers-reduced-motion`; text is always inserted with `textContent`, and Markdown
  is rendered on the server with raw HTML disabled.

## Security notes

- The API never runs learner input; it only parses it.
- Correct answers, explanations and distractor metadata are never sent before an answer is
  submitted (covered by tests).
- Caddy sends a strict Content-Security-Policy (`script-src 'self'`, no inline scripts).
- Compose defaults (database password, `APP_SECRET_KEY`) are for local development only;
  set real values in `.env` before running anywhere else.

## Not built yet

- Accounts and server-side progress (the database is prepared but unused).
- Hands-on labs with a real terminal. The intended design: a separate sandbox service running
  each session in a locked-down container (gVisor runtime, no network, non-root, CPU/memory/
  process limits, automatic cleanup), checking the resulting system state rather than the
  commands typed. The web API must never get access to the Docker socket.
- More content: networking, processes, packages, services and logs, scripting, and theory
  pages for Docker, Kubernetes and Cloud.
