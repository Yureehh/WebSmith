# Build Brief For {business_name}

Read this file first, then `SOURCE_INDEX.md` and every file in `source_documents/`.

## Fast Start

```text
Read BUILD_BRIEF.md, SOURCE_INDEX.md, and source_documents/.
Do not build yet. Give me:
1. the source-backed mission/personality;
2. what the current online presence does not fully express;
3. 3 visual directions;
4. the recommended direction for a specific, modern static website.
```

After approving the direction:

```text
Approved. Build only inside site/.
Use only source-backed facts.
List assumptions and missing facts in site/DECISIONS.md.
Create site/README.md and site/DECISIONS.md.
```

## Business Context

{business_context}

## Source Rules

- Use `SOURCE_INDEX.md` and `source_documents/` as the factual base.
- Inspect the current website when available, but use it as context only.
- Preserve recognizable identity; do not clone design or copy long text.
- Do not invent awards, staff names, prices, opening hours, certifications, reviews, or legal details.
- Never insult the current website or online presence.

## Build Rules

- Edit only `{site_path}` unless creating a zip in `{exports_path}`.
- Prefer plain static HTML/CSS/JS. Use Vite only if it materially helps.
- No backend, database, auth, tracking, automatic email, or hidden integrations.
- Keep CTAs source-safe: call, WhatsApp, book, reserve, visit, or request info only when supported.
- Put final generated assets in `site/assets/`; keep rejected/source experiments outside `site/`.

## Creative Rules

Choose 3-5 tone adjectives and make them visible in copy, layout, color, typography, imagery, and CTAs. Examples: warm, refined, practical, premium, playful, trustworthy, artisanal, cinematic, local.

Avoid generic templates. The site should feel specific to this business category, location, and source material.

## Output

```text
site/
  README.md
  DECISIONS.md
  index.html
  src/
    styles.css
    main.js
  assets/
```

`site/DECISIONS.md` must list tone, source-backed facts used, assumptions, missing info, and generated assets/prompts.

## Acceptance

- Works by opening `index.html` or with a simple local server.
- Mobile text/layout does not overflow.
- Factual claims are traceable to sources or listed as assumptions.
- CTAs are visible and useful.
- No tracking pixels or automatic sending are added.
