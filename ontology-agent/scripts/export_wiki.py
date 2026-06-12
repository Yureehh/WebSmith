from pathlib import Path
from company_ontology_agent.config.project_config import load_project_config
from company_ontology_agent.wiki.exporter import WikiExporter
from company_ontology_agent.workflows.build_graph import repository_for

root = Path.cwd()
config = load_project_config(root)
graph = repository_for(root, config, dry_run=True).read_graph(config.project_slug)
files = WikiExporter().export(graph, root / config.wiki.output_path)
print(f'Exported {len(files)} wiki files')
