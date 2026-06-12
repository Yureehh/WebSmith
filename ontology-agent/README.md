# ontology-agent

Markdown wiki output is enabled.

## Daily Commands

```bash
docker compose up -d
cp .env.example .env
make doctor
make dry-run
make sync-neo4j
make wiki
```

The `wiki/` folder is project-local and intended to be committed. `data/normalized/`, `data/processed/`, and Graphify internals are rebuildable and ignored by git.
