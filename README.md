# Django Auth + Media Backend

Two small Django services live here:
- Auth server: registration + login, issues JWTs (DRF + SimpleJWT).
- Backend server: accepts authenticated uploads (images/audio) and lists files.

They run separately but share a signing key through env vars. Nothing fancy—just enough to test a token flow end to end.

## Tech
- Django 5 + Django REST Framework
- SimpleJWT on the auth side, PyJWT-based check on the backend
- SQLite for dev
- `django-cors-headers` for local testing

## Layout
- `auth_server/` – Django project with an `accounts` app
- `backend_server/` – Django project with a `mediafiles` app
- `docker-compose.yml` – spins up both
- `.env.example` – copy to `.env` before running

## Env
Copy `.env.example` to `.env` and tweak as needed. The important bits:
- `JWT_SIGNING_KEY` – shared secret used by both services. In real life, keep this out of the repo and rotate it.
- `AUTH_DJANGO_SECRET_KEY`, `BACKEND_DJANGO_SECRET_KEY` – separate Django secrets.
- `AUTH_DB_URL`, `BACKEND_DB_URL` – DB URLs. Defaults are local SQLite files.

For local dev, `DJANGO_DEBUG=True` and a broad `DJANGO_ALLOWED_HOSTS` are fine.

## Run with Docker (quickest)
1) Copy env: `cp .env.example .env`
2) Bring everything up: `docker compose up --build`

You’ll get:
- Auth server at http://localhost:8001
- Backend server at http://localhost:8002

Uploaded media goes to `/app/media` in the backend container (mounted volume).

## Run locally (optional)
If you prefer venvs, run each service on its own.

Auth server:
- `cd auth_server`
- `python -m venv .venv && source .venv/bin/activate`
- `pip install -r requirements.txt`
- export your env (or drop a `.env` here and `source` it)
- `python manage.py migrate`
- `python manage.py runserver 0.0.0.0:8001`

Backend server:
- `cd backend_server`
- `python -m venv .venv && source .venv/bin/activate`
- `pip install -r requirements.txt`
- export your env (make sure `SIMPLE_JWT_SIGNING_KEY` matches the auth server)
- `python manage.py migrate`
- `python manage.py runserver 0.0.0.0:8002`

## API quick notes
Use the Swagger UI each service exposes:

- Auth docs: http://localhost:8001/api/docs/ (schema at `/api/schema/`)
- Backend docs: http://localhost:8002/api/docs/ (schema at `/api/schema/`)


## Admin

Both services ship with Django admin enabled:
- Auth admin: http://localhost:8001/admin/
- Backend admin: http://localhost:8002/admin/

You can auto-create a superuser on startup by setting these in your `.env` (applies to both services):
```
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=admin123
DJANGO_SUPERUSER_EMAIL=admin@example.com
```

Note: the entrypoints run migrations and collectstatic as usual.
