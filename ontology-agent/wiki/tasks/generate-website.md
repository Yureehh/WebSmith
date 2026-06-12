---
id: entity_0f6699acadf46189
type: Task
project: ontology-agent
graph_node_id: entity_0f6699acadf46189
sources:
- span_2ef30ca0ceafa9e5
- span_63ffe0bbb61cea27
---

# Task: Generate website

## Summary

Generate website is tracked as a Task in the project graph. It has 2 outgoing and 1 incoming validated relationships.

## Aliases

- None

## Outgoing Relationships

- `generates` -> [[generated-workspace|Generated workspace]] (confidence 0.86, validated)
- `generates` -> [[website-projects-id-slug|website-projects/<id>-<slug>/]] (confidence 0.86, validated)

## Incoming Relationships

- [[daily-flow|Daily Flow]] -> `contains` (confidence 0.98, validated)

## Evidence

- `span_2ef30ca0ceafa9e5`: # Claude Code VS Code Workflow  Use this for building a website from a WebSmith workspace.  ## Flow  1. In WebSmith, enrich the lead and click `Generate website`. 2. Open the generated `website-projects/<id>-<slug>/` folder in VS Code. 3...
- `span_63ffe0bbb61cea27`: # WebSmith Operating Playbook  This is the daily workflow reference. Keep it short, operational, and source-backed.  ## Daily Flow  1. Search an Italian area by location, radius, optional business name, and optional activity types. 2. Us...
