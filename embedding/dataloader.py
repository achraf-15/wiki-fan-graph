# embedding/dataloader.py

import os
import json

def load_all_chunks(metadata_dir):
    """Load all JSON files and concatenate all chunks."""
    all_chunks = []
    for fname in os.listdir(metadata_dir):
        if fname.endswith('data.json'):
            with open(os.path.join(metadata_dir, fname), 'r', encoding='utf-8') as f:
                chunks = json.load(f)
                all_chunks.extend(chunks)
    return all_chunks


def batch_chunks(chunks, batch_size=32):
    """Yield batches of the same number of chunks."""
    for i in range(0, len(chunks), batch_size):
        if i+batch_size < len(chunks):
            yield chunks[i:i+batch_size]
        else:
            yield chunks[i:]
