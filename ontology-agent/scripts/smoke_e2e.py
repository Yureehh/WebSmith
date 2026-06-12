import argparse
from pathlib import Path
from company_ontology_agent.ingestion.folder import ingest_folder
from company_ontology_agent.workflows.build_graph import build_graph, repository_for
from company_ontology_agent.config.project_config import load_project_config
from company_ontology_agent.wiki.exporter import WikiExporter

parser = argparse.ArgumentParser()
parser.add_argument('--dry-run', action='store_true')
args = parser.parse_args()
root = Path.cwd()
config = load_project_config(root)
ingest_folder(root / 'data/raw', root)
result = build_graph(root, dry_run=args.dry_run)
repo = repository_for(root, config, dry_run=args.dry_run)
graph = repo.read_graph(config.project_slug)
files = WikiExporter().export(graph, root / config.wiki.output_path)
print(
    f'entities={len(result.graph.entities)} '
    f'assertions={len(result.graph.assertions)} '
    f'wiki_files={len(files)}'
)
