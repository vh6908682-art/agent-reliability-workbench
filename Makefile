
.PHONY: dev api web test-api test-web lint-api lint-web db-up db-down

dev:

	docker compose up --build

db-up:

	docker compose up -d db

db-down:

	docker compose down

api:

	cd apps/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

web:

	cd apps/web && npm run dev

test-api:

	cd apps/api && pytest

test-web:

	cd apps/web && npm test

lint-api:

	cd apps/api && ruff check .

lint-web:

	cd apps/web && npm run lint

