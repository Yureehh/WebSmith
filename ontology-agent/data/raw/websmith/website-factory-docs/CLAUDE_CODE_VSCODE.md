# Claude Code VS Code Workflow

Use this for building a website from a WebSmith workspace.

## Flow

1. In WebSmith, enrich the lead and click `Generate website`.
2. Open the generated `website-projects/<id>-<slug>/` folder in VS Code.
3. Open Claude Code from that folder, not from the WebSmith repo root.
4. Paste the planning prompt from `BUILD_BRIEF.md`.
5. Refine the direction in plain language, for example:

```text
Use the strongest direction, but make it warmer, more artisanal, more cinematic, and less corporate.
Preserve recognizable identity. Do not clone the current site. Do not invent facts.
```

6. Approve the build prompt from `BUILD_BRIEF.md`.
7. Preview:

```bash
python3 -m http.server 4173 -d site
```

8. QA:

```text
Review desktop and mobile. Fix layout issues, weak copy, generic sections, spacing problems, and unsupported claims. Ensure every factual claim is traceable to source_documents/ or listed in site/DECISIONS.md.
```

9. Export only `site/` into `exports/` if needed.
10. Import the `site/` path, zip path, or preview URL back into WebSmith.
