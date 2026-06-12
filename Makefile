.PHONY: install migrate dev-backend dev-frontend lint test build-frontend backup-db export-projects smoke-openai smoke-openai-web

install:
	cd backend && uv sync
	cd frontend && npm install

migrate:
	cd backend && uv run alembic upgrade head

dev-backend:
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev -- --host 0.0.0.0

lint:
	cd backend && uv run ruff check .
	cd backend && uv run ruff format --check .
	cd frontend && npm run lint

test:
	cd backend && uv run pytest

build-frontend:
	cd frontend && npm run build

backup-db:
	mkdir -p backups
	cp backend/.data/websmith.sqlite3 backups/websmith-$$(date +%Y%m%d-%H%M%S).sqlite3

export-projects:
	mkdir -p backups
	tar -czf backups/website-projects-$$(date +%Y%m%d-%H%M%S).tar.gz website-projects

smoke-openai:
	cd backend && uv run python scripts/openai_smoke.py

smoke-openai-web:
	cd backend && uv run python scripts/openai_smoke.py --web-search
