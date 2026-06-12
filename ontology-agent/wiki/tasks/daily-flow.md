---
id: entity_4da8c0b69b7cafcf
type: Task
project: ontology-agent
graph_node_id: entity_4da8c0b69b7cafcf
sources:
- span_63ffe0bbb61cea27
---

# Task: Daily Flow

## Summary

Daily Flow is tracked as a Task in the project graph. It has 11 outgoing and 1 incoming validated relationships.

## Aliases

- None

## Outgoing Relationships

- `contains` -> [[closeout-statuses|Closeout statuses]] (confidence 0.95, validated)
- `contains` -> [[draft-first-email|Draft first email]] (confidence 0.95, validated)
- `contains` -> [[enrich|Enrich]] (confidence 0.98, validated)
- `contains` -> [[final-site-import|Final site import]] (confidence 0.95, validated)
- `contains` -> [[generate-website|Generate website]] (confidence 0.98, validated)
- `contains` -> [[italian-area-search|Italian area search]] (confidence 0.98, validated)
- `contains` -> [[lead-evidence-confirmation|Lead evidence confirmation]] (confidence 0.95, validated)
- `contains` -> [[manual-send|Manual send]] (confidence 0.95, validated)
- `validates` -> [[lead-queue|Lead queue]] (confidence 0.90, validated)
- `validates` -> [[map-coverage|Map coverage]] (confidence 0.90, validated)
- `validates` -> [[provider-warnings|Provider warnings]] (confidence 0.90, validated)

## Incoming Relationships

- [[websmith-operating-playbook|WebSmith Operating Playbook]] -> `documents` (confidence 0.95, validated)

## Evidence

- `span_63ffe0bbb61cea27`: # WebSmith Operating Playbook  This is the daily workflow reference. Keep it short, operational, and source-backed.  ## Daily Flow  1. Search an Italian area by location, radius, optional business name, and optional activity types. 2. Us...
