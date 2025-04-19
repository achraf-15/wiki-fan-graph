import os
import json


def load_data_json_files(directory):
    """Load all JSON files from the specified directory."""
    data_files = [f for f in os.listdir(directory) if f.endswith('data.json')]
    batch_data = []
    for file in data_files:
        with open(os.path.join(directory, file), 'r', encoding='utf-8') as f:
            batch_data.extend(json.load(f))
    return batch_data

def load_page_json_files(directory): 
    """Load all JSON files from the specified directory."""
    data_files = [f for f in os.listdir(directory) if f.endswith('page.json')]
    batch_data = []
    for file in data_files:
        with open(os.path.join(directory, file), 'r', encoding='utf-8') as f:
            content = json.load(f)
            batch_data.append(content)
    return batch_data

def load_graph_json_files(directory): 
    """Load JSON files in batches from the specified directory."""
    graph_files = [f for f in os.listdir(directory) if f.endswith('graph.json')]
    batch_graph = {}
    for file in graph_files:
        with open(os.path.join(directory, file), 'r', encoding='utf-8') as f:
            batch_graph.update(json.load(f))
    return batch_graph

def load_chunk_indices(directory): 
    """Load JSON files in batches from the specified directory."""
    filename = "chunk_subs.json"
    file_path = os.path.join(directory, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        chunk2subs = json.load(f)
    return chunk2subs
