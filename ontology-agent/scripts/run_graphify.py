from pathlib import Path
from company_ontology_agent.config.project_config import load_project_config
from company_ontology_agent.extraction.graphify_adapter import GraphifyExtractor

root = Path.cwd()
config = load_project_config(root)
extractor = GraphifyExtractor.from_config(root, config)
result = extractor.run(root / config.graphify.input_path, config.project_slug)
print('\n'.join(result.summary_lines()))
