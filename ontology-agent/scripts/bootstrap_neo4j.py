from pathlib import Path
from company_ontology_agent.config.project_config import load_project_config
from company_ontology_agent.workflows.build_graph import repository_for

root = Path.cwd()
config = load_project_config(root)
repo = repository_for(root, config, dry_run=False)
repo.bootstrap()
print('Neo4j bootstrap complete')
