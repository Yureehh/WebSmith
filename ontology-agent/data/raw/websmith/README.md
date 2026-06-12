# WebSmith

WebSmith is a local-first managed-service cockpit for discovering Italian local businesses, qualifying website opportunities, preparing Codex Sites / Codex / Claude Code website workspaces, and managing manual outreach.

It is built for Juri's internal commercial workflow first. It is not a SaaS yet: no auth, no billing, no users, no automatic email sending.

## Current Status

- Local app works with FastAPI, SQLite, React, Vite, Tailwind, and Leaflet.
- Discovery uses OSM/Overpass. Paid map APIs are intentionally not used.
- Searches support activity filters, negative filters, search depth, dedupe, and map coverage metadata.
- Enrichment, outreach drafts, reply drafts, and stronger website briefs require `OPENAI_API_KEY`.
- Website generation creates handoff workspaces under `website-projects/` for Codex Sites, local Codex, and Claude Code.

See `docs/product/PRODUCT_STATUS.md` for the exact feature state.

## Stack

- Backend: FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, SQLite, pytest, Ruff, uv
- Frontend: React, TypeScript, Vite, TanStack Query, TanStack Router, React Hook Form, Zod, Tailwind CSS, Leaflet
- Jobs: persisted SQLite job table with synchronous local v1 workers
- AI: OpenAI API required for enrichment/copy/outreach quality

## Quick Start

```bash
cp .env.example .env
make install
make migrate
make dev-backend
```

In another shell:

```bash
make dev-frontend
```

Backend: http://localhost:8000
Frontend: http://localhost:5173

## Useful Commands

```bash
make lint
make test
make build-frontend
make backup-db
```

## Operating Flow

1. Search an area in Italy by location, radius, optional name, and optional activity types.
2. Inspect map coverage and lead queue.
3. Enrich promising leads with an OpenAI key configured.
4. Generate a website workspace.
5. Open the generated workspace and start from `BUILD_BRIEF.md`.
6. Ask Claude Code, Codex, or Codex Sites to plan first, then build externally inside `site/`.
7. Import the folder, zip, or preview URL back into WebSmith.
8. Draft first email, send manually, and track replies.

## Documentation

Start with `docs/README.md`. The main day-to-day guide is `docs/workflow/OPERATING_PLAYBOOK.md`.

## Optional OpenAI Smoke Checks

These commands are manual and may call the OpenAI API. They are not part of normal tests.

```bash
make smoke-openai
make smoke-openai-web
```

## Private Files

The `private/` folder is gitignored. It contains local business templates such as:

- `private/contracts/contratto-sito-web-template-it.md`
- `private/marketing/linkedin-posts.md`

These are intentionally not committed.

## Provider Safety

- OSM/Overpass is the zero-cost default discovery path.
- Paid map discovery APIs are intentionally not used.
- Area web-search backup is off by default and can be enabled in Settings.
- Selected-lead `Enrich` can use OpenAI web lookup when `OPENAI_API_KEY` is configured.
- Add `OPENAI_API_KEY` before using enrichment summaries, website handoff brief generation, outreach drafts, or reply drafts.
