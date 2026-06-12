# WebSmith Operating Playbook

This is the daily workflow reference. Keep it short, operational, and source-backed.

## Daily Flow

1. Search an Italian area by location, radius, optional business name, and optional activity types.
2. Use include filters only when the area is too broad.
3. Keep negative filters active for low-fit categories such as fuel, banks, public offices, post offices, churches, police, pharmacies, supermarkets, schools, and hospitals.
4. Check map coverage, provider warnings, and the lead queue.
5. Select promising public-facing leads with missing or weak website/contact evidence.
6. Click `Enrich` one lead at a time to collect website, contact, source, and qualitative context.
7. Confirm evidence: website, public contact, source URLs, and any ambiguity warning.
8. Click `Generate website` only for leads worth a concrete proposal.
9. Open the generated workspace and start external builders from `BUILD_BRIEF.md`.
10. Build externally with Codex Sites, local Codex, Claude Code, or another builder.
11. Import the final `site/` path, zip, or preview URL back into WebSmith.
12. Click `Draft first email`.
13. Send manually outside WebSmith.
14. Click `I sent email` only after the manual send.
15. Paste every reply into WebSmith and draft replies as needed.
16. Close with `Follow up later`, `Won`, `Lost`, `Archive`, or `Do not contact`.

## Search Limit Meaning

WebSmith uses an internal fresh-lead target for each search. Known businesses do not count toward that target, including enriched, active, archived, won, lost, and do-not-contact leads.

Example: if an area already has 80 known leads and the internal target is 200, WebSmith skips the 80 known leads and still tries to add up to 200 new leads from the provider.

## First Outreach Batch

After the first successful website draft, build only 3-5 more drafts before sending a large wave. Start outreach with 5-10 businesses maximum.

Choose leads where:

- the business is public-facing;
- the draft is clearly better than the current online presence;
- the contact path is public and reasonable;
- the lead is not marked do-not-contact;
- the email can mention one real public observation.

## Draft QA

Before outreach, check:

- the site feels specific to the business, not template-like;
- factual claims are source-backed or listed as assumptions;
- missing facts are not invented;
- contact CTA is visible;
- mobile layout is strong;
- current-site identity is respected without copying the old design;
- `site/DECISIONS.md` explains tone, sources, assumptions, and assets.

## Reply And Closeout

When someone replies:

1. Click `I received answer` or `Paste answer + draft reply`.
2. Paste the full reply.
3. Draft a response.
4. Set a follow-up date if needed.
5. Before paid delivery, confirm scope, domain/hosting ownership, pricing, contract/SOW, and approval path.
6. Close as won, lost, archive, or do-not-contact when appropriate.

## Rules

- Never send automatically from WebSmith.
- Do not contact leads marked do-not-contact.
- Keep source-backed claims only.
- Prefer B2C businesses where public trust and conversion matter.
- Use client-owned hosting by default.
- Area web-search backup is off by default because it can incur API/tool usage.
- Selected-lead `Enrich` can use OpenAI web lookup when `OPENAI_API_KEY` is configured.
