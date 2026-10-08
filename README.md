# ShellCraft

Learn Linux, Docker, Kubernetes and cloud through short quizzes with real command outputs,
written-command exercises and an explanation for every answer, wrapped in a pixel-art RPG look.

The learning content is in Greek; code and documentation are in English.

## What's in it

- **Four sections**: Linux, Docker, Kubernetes and Cloud. Each opens with an **intro** (what
  the technology is, why it was created, where it runs today), then **theory**, then **quizzes**.
- **14 quizzes, 167 questions**, ordered from easy to hard inside every quiz: concepts first,
  then writing commands, then troubleshooting and scenarios. Each question shows its
  difficulty (easy / medium / hard).
- **Question types**: multiple choice, pick the command, fill in the blank, *write the
  command*, read the output, and put the steps in order.
- **Written commands are checked, never executed.** The evaluator understands option order,
  bundled flags (`-rf`), long and short spellings, command aliases (`docker ps` =
  `docker container ls`) and `./file` = `file`, and explains what went wrong.
- **Real outputs**: every command output and error message in a question was captured on a real
  system (Debian 13.7, Docker 29.5.2, Kubernetes v1.37.1), and facts cite official
  documentation.
- One question per page with back/next, score, best results and stars kept in the browser,
  8-bit sounds and section transitions.

## Quick start

Requirements: Docker with Docker Compose v2, and `make`.

```bash
make dev        # http://localhost:8080
```

Optionally copy `.env.example` to `.env` first to change the defaults.

| Command | What it does |
|---|---|
| `make dev` / `make up` | Build and run the proxy, API and database (foreground / background) |
| `make down` | Stop everything |
| `make test` | Run the test suite |
| `make lint` | Lint and format check (ruff) |
| `make content-validate` | Validate all content (schemas, references, sources, question order, command test cases) |

API docs (outside production): http://localhost:8080/api/docs

## Adding content

All learning material lives in [`content/`](content) as YAML and Markdown; no code changes are
needed. Every *write the command* question lists commands that must be accepted and commands
that must be rejected, and `make content-validate` runs them through the real evaluator.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for how it all fits together.

## License

ShellCraft is released under the [MIT License](LICENSE).

The pixel font [Press Start 2P](frontend/assets/fonts) is © The Press Start 2P Project Authors
and licensed under the SIL Open Font License 1.1 (see `frontend/assets/fonts/OFL-pressstart2p.txt`).
