# knowledge_graph\knowledge_graph.py

import os
import json
import networkx as nx
import numpy as np
from tqdm import tqdm
from networkx.readwrite import json_graph

from knowledge_graph.utils import load_data_json_files, load_graph_json_files, load_page_json_files


class KnowledgeGraph:
    def __init__(self, data_dir, metadata_dir, page_dir, graph_dir, EmbeddingDatabase,verbose=1):
        self.data_dir = data_dir
        self.metadata_dir = metadata_dir
        self.page_dir = page_dir
        self.graph_dir = graph_dir
        self.db = EmbeddingDatabase()
        self.graph = nx.DiGraph()
        self.chunk2subs = None
        self.chunk_graph = None
        self.page_graph = None
        self.verbose = verbose

    def setup(self):
        """Setup and build the initial knowledge graph from metadata and edge definitions."""

        metadata_data = load_data_json_files(self.metadata_dir)
        graph_data = load_graph_json_files(self.graph_dir)
        page_data = load_page_json_files(self.page_dir)

        valid_docs = set()
        valid_chunks = set()

        # Add nodes
        for chunk in metadata_data:
            chunk_id = chunk['chunk_id']
            title = chunk['title']
            category = chunk['category']
            section = chunk['section']

            self.graph.add_node(chunk_id, title=title, category=category, section=section, type='chunk')
            valid_chunks.add(chunk_id)

        for page in page_data:
            title = page['title']
            category = page['category']

            self.graph.add_node(title, category=category, type='document')
            valid_docs.add(title)

        if self.verbose:
            print("Valid Document Nodes:", len(valid_docs))
            print("Valid Chunk Nodes:", len(valid_chunks))

        # Add edges
        for source, targets in graph_data.items():
            for target, label in targets:
                if target in valid_docs or label == "chunk":
                    self.graph.add_edge(source, target, label=label)

    def build(self, top_k=3):
        """Connect chunk nodes directly using top-k nearest neighbors based on vector similarity."""
        G = self.graph.copy()
        nodes_to_remove = []

        for chunk_node, data in tqdm(G.nodes(data=True), desc="Connecting Chunk Nodes", disable=(self.verbose<2)):
            if data.get('type') != 'chunk':
                continue

            chunk_title = data.get('title')
            chunk_embedding = self.db.get_embedding(chunk_node)
            if not isinstance(chunk_embedding,np.ndarray):
                nodes_to_remove.append(chunk_node)
                continue

            # Get associated document nodes
            connected_docs = [(target, d['label']) for _, target, d in G.out_edges(chunk_node, data=True)]

            for doc_node, label in connected_docs:
                # Connect the pages
                G.add_edge(chunk_title, doc_node, label=label)
                related_chunks = set(G.successors(doc_node)) - {chunk_node}
                if not related_chunks:
                    continue

                top_chunks = self.db.dense_search(related_chunks, chunk_embedding, top_k)
                for (rel_chunk, similarity) in top_chunks:
                    G.add_edge(chunk_node, rel_chunk, weight=similarity, label=label)

        chunk_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'chunk']
        page_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'document']

        self.chunk_graph = G.subgraph(chunk_nodes)
        self.page_graph = G.subgraph(page_nodes)

    
    def save(self, outdir: str, graph_type: str = 'chunk'):
        """
        Save either the chunk knowledge graph or the page knowledge graph graph to disk.

        Args:
            path: Path to save the graph JSON.
            graph_type: 'chunk' to save self.chunk_graph, 'page' to save self.page_graph.
        """
        os.makedirs(f"{outdir}/knowledge_graph", exist_ok=True)
        
        if graph_type == 'chunk':
            G = self.chunk_graph
            filename = "chunk_knowledge_graph.json"
            file_path = os.path.join(f"{outdir}/knowledge_graph", filename)
        elif graph_type == 'page':
            G = self.page_graph
            filename = "page_knowledge_graph.json"
            file_path = os.path.join(f"{outdir}/knowledge_graph", filename)
        else:
            raise ValueError("graph_type must be 'chunk' or 'page'")

        data = json_graph.node_link_data(G, edges="links")

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        if self.verbose>=2:
            print(f"Graph saved to {file_path}")

    def load(self, outdir: str, graph_type: str = 'chunk'):
        """
        Load a graph from disk and replace the internal knowledge graph.
        Args:
            path: Path to the graph JSON file.
        """
        if graph_type == 'chunk':
            filename = "chunk_knowledge_graph.json"
            file_path = os.path.join(f"{outdir}/knowledge_graph", filename)
        elif graph_type == 'page':
            filename = "page_knowledge_graph.json"
            file_path = os.path.join(f"{outdir}/knowledge_graph", filename)
        else:
            raise ValueError("graph_type must be 'chunk' or 'page'")

        with open(file_path, 'r') as f:
            data = json.load(f)

        if graph_type == 'chunk':
            self.chunk_graph = json_graph.node_link_graph(data, edges="links")
        elif graph_type == 'page':
            self.page_graph = json_graph.node_link_graph(data, edges="links")
        else:
            raise ValueError("graph_type must be 'chunk' or 'page'")    
        
        if self.verbose>=2:
            print(f"Graph loaded from {file_path}")
