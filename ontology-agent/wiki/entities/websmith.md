---
id: entity_d9666b777644b945
type: Technology
project: ontology-agent
graph_node_id: entity_d9666b777644b945
sources:
- span_2ef30ca0ceafa9e5
- span_63ffe0bbb61cea27
- span_64c2cfa728545a2d
- span_80648b96719fbc77
---

# Technology: WebSmith

## Summary

WebSmith is tracked as a Technology in the project graph. It has 52 outgoing and 2 incoming validated relationships.

## Aliases

- None

## Outgoing Relationships

- `blocks` -> [[auth|Auth]] (confidence 0.90, validated)
- `blocks` -> [[automatic-email-sending|Automatic email sending]] (confidence 0.90, validated)
- `blocks` -> [[automatic-sending|Automatic sending]] (confidence 0.98, validated)
- `blocks` -> [[billing|Billing]] (confidence 0.90, validated)
- `blocks` -> [[paid-map-apis|Paid map APIs]] (confidence 0.95, validated)
- `blocks` -> [[saas-tenancy|SaaS tenancy]] (confidence 0.95, validated)
- `blocks` -> [[users|Users]] (confidence 0.90, validated)
- `blocks` -> [[auth|auth]] (confidence 0.95, validated)
- `blocks` -> [[automatic-email-sending|automatic email sending]] (confidence 0.95, validated)
- `blocks` -> [[billing|billing]] (confidence 0.95, validated)
- `blocks` -> [[finalized-client-contracts|finalized client contracts]] (confidence 0.95, validated)
- `blocks` -> [[legal-advice|legal advice]] (confidence 0.95, validated)
- `blocks` -> [[paid-map-discovery-apis|paid map discovery APIs]] (confidence 0.95, validated)
- `blocks` -> [[public-deployment|public deployment]] (confidence 0.95, validated)
- `blocks` -> [[user-accounts|user accounts]] (confidence 0.95, validated)
- `classifies` -> [[website-opportunities|Website opportunities]] (confidence 0.96, validated)
- `classifies` -> [[website-opportunities|Website opportunities]] (confidence 0.90, validated)
- `classifies` -> [[market-classification|market classification]] (confidence 0.95, validated)
- `discovers` -> [[italian-local-businesses|Italian local businesses]] (confidence 0.99, validated)
- `discovers` -> [[local-italian-businesses|local Italian businesses]] (confidence 0.95, validated)
- `enriches` -> [[lead|lead]] (confidence 0.88, validated)
- `generates` -> [[claude-code-website-workspaces|Claude Code website workspaces]] (confidence 0.94, validated)
- `generates` -> [[codex-sites-website-workspaces|Codex Sites website workspaces]] (confidence 0.94, validated)
- `generates` -> [[codex-website-workspaces|Codex website workspaces]] (confidence 0.94, validated)
- `generates` -> [[outreach-drafts|Outreach drafts]] (confidence 0.86, validated)
- `generates` -> [[brief-workspace|brief/workspace]] (confidence 0.95, validated)
- `generates` -> [[external-website-workspaces|external website workspaces]] (confidence 0.95, validated)
- `implements` -> [[local-managed-service-cockpit|local managed-service cockpit]] (confidence 0.95, validated)
- `manages` -> [[manual-outreach|Manual outreach]] (confidence 0.98, validated)
- `manages` -> [[manual-outreach|Manual outreach]] (confidence 0.95, validated)
- `owned_by` -> [[juri-s-internal-commercial-workflow|Juri's internal commercial workflow]] (confidence 0.80, validated)
- `reads_from` -> [[provider|Provider]] (confidence 0.90, validated)
- `reads_from` -> [[preview-url|preview URL]] (confidence 0.84, validated)
- `reads_from` -> [[site-path|site path]] (confidence 0.84, validated)
- `reads_from` -> [[zip-path|zip path]] (confidence 0.84, validated)
- `related_to` -> [[saas|SaaS]] (confidence 0.70, validated)
- `stores` -> [[lead-storage|lead storage]] (confidence 0.90, validated)
- `supports` -> [[openai-backed-enrichment|OpenAI-backed enrichment]] (confidence 0.95, validated)
- `supports` -> [[explicit-enrichment-action|explicit enrichment action]] (confidence 0.95, validated)
- `supports` -> [[manual-only-crm-actions|manual-only CRM actions]] (confidence 0.95, validated)
- `supports` -> [[outreach|outreach]] (confidence 0.90, validated)
- `supports` -> [[reply-drafting|reply drafting]] (confidence 0.95, validated)
- `supports` -> [[web-search-website-lookup|web-search website lookup]] (confidence 0.95, validated)
- `supports` -> [[website-workspace-generation|website workspace generation]] (confidence 0.95, validated)
- `uses` -> [[fastapi|FastAPI]] (confidence 0.99, validated)
- `uses` -> [[internal-fresh-lead-target|Internal fresh-lead target]] (confidence 0.98, validated)
- `uses` -> [[leaflet|Leaflet]] (confidence 0.99, validated)
- `uses` -> [[osm-overpass-discovery|OSM/Overpass discovery]] (confidence 0.95, validated)
- `uses` -> [[react|React]] (confidence 0.99, validated)
- `uses` -> [[sqlite|SQLite]] (confidence 0.99, validated)
- `uses` -> [[tailwind|Tailwind]] (confidence 0.99, validated)
- `uses` -> [[vite|Vite]] (confidence 0.99, validated)

## Incoming Relationships

- [[final-site-import|Final site import]] -> `writes_to` (confidence 0.95, validated)
- [[reply-handling|Reply handling]] -> `writes_to` (confidence 0.95, validated)

## Evidence

- `span_2ef30ca0ceafa9e5`: # Claude Code VS Code Workflow  Use this for building a website from a WebSmith workspace.  ## Flow  1. In WebSmith, enrich the lead and click `Generate website`. 2. Open the generated `website-projects/<id>-<slug>/` folder in VS Code. 3...
- `span_63ffe0bbb61cea27`: # WebSmith Operating Playbook  This is the daily workflow reference. Keep it short, operational, and source-backed.  ## Daily Flow  1. Search an Italian area by location, radius, optional business name, and optional activity types. 2. Us...
- `span_64c2cfa728545a2d`: # WebSmith Product Status  WebSmith is a local managed-service cockpit for discovering local Italian businesses, qualifying website opportunities, preparing external website workspaces, and managing manual outreach.  ## Works Now  - OSM/...
- `span_80648b96719fbc77`: # WebSmith  WebSmith is a local-first managed-service cockpit for discovering Italian local businesses, qualifying website opportunities, preparing Codex Sites / Codex / Claude Code website workspaces, and managing manual outreach.  It i...
