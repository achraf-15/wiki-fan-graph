# crawler/writers/json_writer.py

import json
import os
from dataclasses import asdict
from typing import List
from crawler.schemas import ChunkData, DocumentData
from crawler.utils.helpers import clean_filename

def save_data(chunks: List[ChunkData], title: str, outdir="data"):
    """Saves extracted data to a JSON file."""
    os.makedirs(f"{outdir}/metadata", exist_ok=True)
    filename = f"{clean_filename(title)}_data.json"
    file_path = os.path.join(f"{outdir}/metadata", filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump([asdict(c) for c in chunks], f, indent=2, ensure_ascii=False)

def save_doc(doc: DocumentData, title: str, outdir="data"):
    """Saves extracted doc to a JSON file."""
    os.makedirs(f"{outdir}/pages", exist_ok=True)
    filename = f"{clean_filename(title)}_page.json"
    file_path = os.path.join(f"{outdir}/pages", filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(asdict(doc), f, indent=2, ensure_ascii=False)

def save_graph(graph: dict, title: str, outdir="data"):
    """Saves extracted graph to a JSON file."""
    os.makedirs(f"{outdir}/graph", exist_ok=True)
    filename = f"{clean_filename(title)}_graph.json"
    file_path = os.path.join(f"{outdir}/graph", filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)

def save_url(url: str, outdir="data"):
    """Saves extracted data to a JSON file."""
    os.makedirs(f"{outdir}", exist_ok=True)
    filename = f"parsed_urls.json"
    file_path = os.path.join(f"{outdir}", filename)
    
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(url + "\n")

def load_saved_urls(outdir="data"):
    """Load all URLs from saved metadata JSON files."""
    filename = f"parsed_urls.json"
    file_path = os.path.join(f"{outdir}", filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    return urls

def delete_saved_urls(outdir="data"):
    """Load all URLs from saved metadata JSON files."""
    filename = f"parsed_urls.json"
    file_path = os.path.join(f"{outdir}", filename)
    if os.path.exists(file_path):
        os.remove(file_path)

