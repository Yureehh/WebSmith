---
id: entity_bb3d765ab3f6532d
type: Task
project: ontology-agent
graph_node_id: entity_bb3d765ab3f6532d
sources:
- span_63ffe0bbb61cea27
- span_64c2cfa728545a2d
---

# Task: Enrich

## Summary

Enrich is tracked as a Task in the project graph. It has 2 outgoing and 2 incoming validated relationships.

## Aliases

- None

## Outgoing Relationships

- `enriches` -> [[public-facing-leads|Public-facing leads]] (confidence 0.90, validated)
- `uses` -> [[openai-web-lookup|OpenAI web lookup]] (confidence 0.95, validated)

## Incoming Relationships

- [[daily-flow|Daily Flow]] -> `contains` (confidence 0.98, validated)
- [[selected-lead-web-lookup|selected-lead web lookup]] -> `runs_on` (confidence 0.95, validated)

## Evidence

- `span_63ffe0bbb61cea27`: # WebSmith Operating Playbook  This is the daily workflow reference. Keep it short, operational, and source-backed.  ## Daily Flow  1. Search an Italian area by location, radius, optional business name, and optional activity types. 2. Us...
- `span_64c2cfa728545a2d`: # WebSmith Product Status  WebSmith is a local managed-service cockpit for discovering local Italian businesses, qualifying website opportunities, preparing external website workspaces, and managing manual outreach.  ## Works Now  - OSM/...
