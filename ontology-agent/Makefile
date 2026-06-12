SHELL := /bin/bash
ONTOLOGY_AGENT ?= /Users/yureeh/Dev/ontology-agent-venv/bin/ontology-agent
-include .env
export

.PHONY: ci docs doctor ingest graphify dry-run graph wiki sync-dry-run sync-neo4j full-stack serve smoke-dry-run smoke-neo4j test

ci:
	uv run --extra dev pytest
	uv run --extra dev ruff check .
	uv run --extra dev mypy
	uv run --extra dev mkdocs build --strict
	uv build

docs:
	uv run --extra dev mkdocs serve

doctor:
	$(ONTOLOGY_AGENT) doctor --strict

ingest:
	$(ONTOLOGY_AGENT) ingest ./data/raw

graphify:
	rm -f graphify-out/GRAPH_REPORT.md
	$(ONTOLOGY_AGENT) graphify run

dry-run:
	$(ONTOLOGY_AGENT) run --dry-run

graph:
	$(ONTOLOGY_AGENT) graph bootstrap
	$(ONTOLOGY_AGENT) build-graph

wiki:
	$(ONTOLOGY_AGENT) export-wiki --neo4j

sync-dry-run:
	$(ONTOLOGY_AGENT) run --dry-run

sync-neo4j:
	$(ONTOLOGY_AGENT) run --neo4j

full-stack:
	$(ONTOLOGY_AGENT) full-stack

serve:
	$(ONTOLOGY_AGENT) serve

smoke-dry-run:
	python scripts/smoke_e2e.py --dry-run

smoke-neo4j:
	python scripts/smoke_e2e.py

test:
	pytest
