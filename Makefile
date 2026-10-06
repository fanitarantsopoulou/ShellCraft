COMPOSE := docker compose -f deploy/compose.yaml --env-file $(or $(wildcard .env),/dev/null)

.PHONY: dev up down logs test content-validate lint fmt migrate revision shell psql

dev:            ## Build and start the full stack (http://localhost:8080)
	$(COMPOSE) up --build

up:
	$(COMPOSE) up --build -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f api

test:           ## Run the backend test suite inside the api container
	$(COMPOSE) run --rm --no-deps api pytest $(ARGS)

content-validate: ## Schema-validate and lint content/
	$(COMPOSE) run --rm --no-deps api python -m cli.content validate

lint:
	$(COMPOSE) run --rm --no-deps api sh -c "ruff check . && ruff format --check ."

fmt:
	$(COMPOSE) run --rm --no-deps api sh -c "ruff check --fix . && ruff format ."

migrate:
	$(COMPOSE) run --rm api alembic upgrade head

revision:       ## make revision m="add users"
	$(COMPOSE) run --rm api alembic revision --autogenerate -m "$(m)"

shell:
	$(COMPOSE) run --rm api bash

psql:
	$(COMPOSE) exec db psql -U $${POSTGRES_USER:-linuxlearn} $${POSTGRES_DB:-linuxlearn}
