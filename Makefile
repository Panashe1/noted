.DEFAULT_GOAL := help
.PHONY: help infra infra-down api web migrate revision test lint typecheck gen-types

help:             ## List available commands
	@grep -hE '^[a-z-]+:.*?##' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'


## Infrastructure
infra:            ## Start Postgres and Redis in Docker
	docker compose up -d --wait

infra-down:       ## Stop infrastructure (data is kept in the volume)
	docker compose down

## Backend
api:              ## Run the FastAPI dev server on :8001
	cd backend && uv run fastapi dev app/main.py --port 8001

migrate:          ## Apply database migrations
	cd backend && uv run alembic upgrade head

revision:         ## Autogenerate a migration: make revision m="add reviews"
	cd backend && uv run alembic revision --autogenerate -m "$(m)"

test:             ## Run backend tests
	cd backend && uv run pytest -q

lint:             ## Lint + format check backend, lint frontend
	cd backend && uv run ruff check . && uv run ruff format --check .
	cd frontend && pnpm lint

typecheck:        ## mypy (strict) + tsc
	cd backend && uv run mypy
	cd frontend && pnpm exec tsc --noEmit

## Frontend
web:              ## Run the Next.js dev server on :3000
	cd frontend && pnpm dev

gen-types:        ## Regenerate frontend API types from the running backend's OpenAPI spec
	cd frontend && pnpm gen:api
