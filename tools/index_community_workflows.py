#!/usr/bin/env python3
import os
import json
import logging

logging.basicConfig(
    filename='/opt/claudio-bot/indexing_v5.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def index_workflows(repo_path, output_file):
    workflows_dir = os.path.join(repo_path, "workflows")
    if not os.path.exists(workflows_dir):
        return

    index = {}
    count = 0

    for root, dirs, files in os.walk(workflows_dir):
        # Look for the metadata file (it starts with "metada" or is "metadata.json")
        meta_file = next((f for f in files if f.startswith("metada") and f.endswith(".json")), None)
        # Look for the workflow file (the largest JSON in the folder that isn't metadata)
        other_jsons = [f for f in files if f.endswith(".json") and f != meta_file and not f.startswith("metada")]
        
        if not other_jsons:
            continue
            
        workflow_file_name = other_jsons[0]
        workflow_path = os.path.join(root, workflow_file_name)
        
        try:
            metadata = {}
            if meta_file:
                with open(os.path.join(root, meta_file), 'r', encoding='utf-8', errors='ignore') as f:
                    metadata = json.load(f)
            
            with open(workflow_path, 'r', encoding='utf-8', errors='ignore') as f:
                workflow_data = json.load(f)
            
            # Basic validation that it IS an n8n workflow
            if "nodes" not in workflow_data:
                continue
                
            name = metadata.get("name") or workflow_data.get("name") or os.path.basename(root).strip()
            
            nodes_used = []
            for node in workflow_data["nodes"]:
                node_type = node.get("type", "").split(".")[-1]
                if node_type and node_type not in nodes_used:
                    nodes_used.append(node_type)
            
            key = os.path.basename(root).strip()
            index[key] = {
                "name": name,
                "description": metadata.get("description", ""),
                "tags": metadata.get("tags", []),
                "nodes": nodes_used,
                "path": os.path.relpath(root, repo_path),
                "workflow_file": workflow_file_name,
                "category": "community"
            }
            count += 1
            if count % 500 == 0:
                logger.info(f"Indexed {count} workflows...")
                
        except Exception:
            pass

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)
    
    logger.info(f"Indexing complete. Total: {count} workflows. Saved to {output_file}")

if __name__ == "__main__":
    import sys
    repo = sys.argv[1] if len(sys.argv) > 1 else "/opt/claudio-bot/external-templates"
    output = sys.argv[2] if len(sys.argv) > 2 else "/opt/claudio-bot/community_index.json"
    index_workflows(repo, output)
