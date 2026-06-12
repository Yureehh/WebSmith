# WebSmith Product Status

WebSmith is a local managed-service cockpit for discovering local Italian businesses, qualifying website opportunities, preparing external website workspaces, and managing manual outreach.

## Works Now

- OSM/Overpass discovery with activity filters, negative filters, search depth, dedupe, and coverage metadata.
- Lead storage in SQLite with discovered, active, and archive queues.
- B2C/B2B/B2C+B2B/unknown market classification from category data.
- Explicit enrichment action with source document storage.
- OpenAI-backed enrichment, web-search website lookup, outreach, and reply drafting when `OPENAI_API_KEY` is configured.
- Manual-only CRM actions: draft, sent marker, received answer, follow-up, do-not-contact, won, lost, archive.
- Compact website workspace generation with one `BUILD_BRIEF.md` for Codex Sites, local Codex, Claude Code, or another external builder.

## Partial

- OSM can miss businesses that are not well mapped.
- Selected-lead web lookup runs during `Enrich` when `OPENAI_API_KEY` is configured.
- Broad area web-search backup is optional and off by default.
- Review extraction is high-level and depends on available public pages.
- Website building is external by design; WebSmith creates the brief/workspace, not the final site.

## Not Included

- User accounts, auth, billing, SaaS tenancy, or public deployment.
- Automatic email sending.
- Paid map discovery APIs.
- Legal advice or finalized client contracts.
