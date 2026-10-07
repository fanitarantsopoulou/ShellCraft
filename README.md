# SudoLearn

Interactive learning platform for Linux, networking, Docker, Kubernetes and cloud,
with an RPG / pixel-art presentation. Learner-facing content is in Greek; code and docs are in English.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the original design analysis.

## What's in it

- **Quizzes** for Linux (6), Docker (3), Kubernetes (3) and Cloud (2) — 167 questions, from first
  commands to troubleshooting. One question per page, back/next, score, results.
- **Question types**: multiple choice, command selection, fill-in, *write the command*, output
  analysis and ordering. Written commands are checked by a command-aware evaluator (flag order,
  aliases such as `docker ps` == `docker container ls`, `./file` == `file`), never executed.
- **Theory** pages, separate from the quizzes.
- Every command output and error message shown in a question was captured on a real system
  (Debian 13.7, Docker 29.5.2, Kubernetes v1.37.1); citations point to official documentation.

## Content

Content lives in `content/` as YAML/Markdown — no code changes needed to add questions.
Each `command_writing` question declares `test_cases` that must pass; validate with:

```bash
make content-validate
```

## Requirements

- Docker with Docker Compose v2
- `make`

## Quick start

```bash
cp .env.example .env   # optional; defaults work for local development
make dev               # http://localhost:8080
```

| Command        | What it does                                   |
|----------------|------------------------------------------------|
| `make dev`     | Build and run proxy + API + PostgreSQL         |
| `make test`    | Run pytest inside the API container            |
| `make lint`    | Ruff lint + format check                       |
| `make migrate` | Apply Alembic migrations                       |
| `make revision m="..."` | Autogenerate a migration              |

API docs (non-production): http://localhost:8080/api/docs
