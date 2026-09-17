# Noted

A social music-review site in the spirit of Letterboxd: log the albums you listen to, rate
them, write about them, follow people, see what they're spinning.

## Stack

| Layer      | Choice                                                                   |
| ---------- | ------------------------------------------------------------------------ |
| API        | FastAPI · SQLAlchemy 2 (async) · asyncpg · Alembic · Pydantic v2         |
| Auth       | Self-managed JWT in httpOnly cookies (15 min access, 30 day refresh)     |
| Data       | Postgres 16 (`pg_trgm` for search) · Redis (provider response cache)     |
| Metadata   | iTunes Search API, behind a swappable `MusicProvider` interface          |
| Web        | Next.js 16 (App Router) · TypeScript · Tailwind v4 · TanStack Query · zod |
| Tooling    | uv · ruff · mypy (strict) · pytest · pnpm · openapi-typescript           |

## Layout

```
noted/
├── backend/
│   ├── app/
│   │   ├── main.py            FastAPI app, CORS, lifespan
│   │   ├── core/              config, db session, cache, security (JWT/argon2), deps
│   │   ├── models/            SQLAlchemy models: User, Artist, Album
│   │   ├── schemas/           Pydantic request/response models
│   │   ├── api/v1/            routers: health, auth, users, albums
│   │   └── services/music/    MusicProvider protocol, iTunes adapter, local-first catalog
│   ├── alembic/               async migrations
│   └── tests/                 pytest, in-memory SQLite, fake provider (no network)
├── frontend/
│   └── src/
│       ├── app/               routes: /, /albums/[id], /u/[username], /login, /register
│       ├── components/        nav, album search, album card, auth form
│       ├── lib/               typed API client (with silent token refresh), hooks
│       └── types/api.d.ts     generated from the backend's OpenAPI spec
├── docker-compose.yml         Postgres + Redis for local dev
└── Makefile                   the commands below
```

## First run

Prerequisites: Docker, [uv](https://docs.astral.sh/uv/), Node 22+, pnpm.

```bash
make infra          # Postgres on :5433, Redis on :6380 (offset to avoid Homebrew defaults)
cd backend && cp .env.example .env && uv sync && cd ..
cd frontend && cp .env.local.example .env.local && pnpm install && cd ..
make migrate        # apply Alembic migrations
```

Then in two terminals:

```bash
make api            # http://localhost:8001  (docs at /api/v1/docs)
make web            # http://localhost:3000
```

The API runs on **8001** rather than 8000 because something else on this machine already
holds 8000. Change it in `Makefile`, `frontend/.env.local` and `frontend/package.json` if
you free that port.

## Everyday commands

```bash
make test           # backend tests (no DB or network needed)
make lint           # ruff + eslint
make typecheck      # mypy --strict + tsc
make revision m="add reviews"   # autogenerate a migration after editing models
make migrate
make gen-types      # regenerate frontend/src/types/api.d.ts (API must be running)
```

## How album search works

1. Search the local `albums` table first (every word must match title or artist, trigram indexed).
2. If fewer than 8 local hits, call iTunes. The raw response is cached in Redis for 24h.
3. Persist everything iTunes returned, so the next search for it never leaves Postgres.

The iTunes Search API is keyless and free, but limited to roughly 20 requests/minute per IP.
Local-first search plus response caching keeps us well under that as the catalog grows.
`Album.apple_id` is the Apple Music album id, so moving to the Apple Music API later is a
new adapter in `app/services/music/`, not a data migration.

## Auth model

- Register/login set two httpOnly cookies: `noted_access` (path `/`) and `noted_refresh`
  (path `/api/v1/auth`). The frontend never sees or stores tokens.
- The API also accepts `Authorization: Bearer <access>` for non-browser clients.
- The web client retries a 401 once after calling `/auth/refresh`.
- Refresh tokens are stateless for now. Add a Redis denylist keyed on `jti` before launch
  if you need logout-everywhere or instant revocation.

## Next milestones

1. Reviews: `reviews` table (half-star rating, text, listened_at, spoilers), CRUD, album page.
2. Social: `follows`, `likes`, activity feed.
3. Lists: `lists` + `list_items`.
4. Diary view and profile stats.
