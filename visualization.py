
import os
import json
import networkx as nx
from networkx.readwrite import json_graph
from config import DATA_DIR

import cudf
import cugraph

import matplotlib.pyplot as plt
import seaborn as sns

class cuGraph:

    def __init__(self, outdir: str = DATA_DIR, graph_type: str = 'chunk',verbose=1):

        self.outdir = outdir
        self.graph_type = graph_type
        self.verbose = verbose
        self.nxGraph = self._load()
        self.edges_df, self.G_cu = self._to_cugraph()
        self.nodes_df = cudf.concat([
                        self.edges_df['src'], self.edges_df['dst']
                    ]).drop_duplicates().reset_index(drop=True).to_frame(name='node')

    def _load(self):
        """
        Load a graph from disk and replace the internal knowledge graph.
        Args:
            path: Path to the graph JSON file.
        """
        if self.graph_type == 'chunk':
            filename = "chunk_knowledge_graph.json"
            file_path = os.path.join(f"{self.outdir}/knowledge_graph", filename)
        elif self.graph_type == 'page':
            filename = "page_knowledge_graph.json"
            file_path = os.path.join(f"{self.outdir}/knowledge_graph", filename)
        else:
            raise ValueError("graph_type must be 'chunk' or 'page'")

        with open(file_path, 'r') as f:
            data = json.load(f)

        if self.graph_type == 'chunk':
            graph = json_graph.node_link_graph(data)
        elif self.graph_type == 'page':
            graph = json_graph.node_link_graph(data)
        else:
            raise ValueError("graph_type must be 'chunk' or 'page'")  
        
        if self.verbose:
            print(f"Graph loaded from {file_path}")

        return graph
    
    def _to_cugraph(self,):
        """
        Convert NetworkX DiGraph to cuGraph format
        """
        edges = nx.to_pandas_edgelist(self.nxGraph)
        gdf_edges = cudf.DataFrame.from_pandas(edges)
        # Rename for cuGraph convention
        gdf_edges = gdf_edges.rename(columns={'source': 'src', 'target': 'dst'})
        # Convert to cuGraph
        G_cu = cugraph.Graph()
        G_cu.from_cudf_edgelist(gdf_edges, source='src', destination='dst', edge_attr='weight', renumber=True)
        return gdf_edges, G_cu
    
    
    def pagerank(self, keep_attr=True, ascending=False):
        pagerank_df = cugraph.pagerank(self.G_cu)
        if keep_attr:
            self.nodes_df = self.nodes_df.merge(pagerank_df, left_on='node', right_on='vertex', how='left')
            self.nodes_df = self.nodes_df.drop(columns=['vertex'])
        return pagerank_df.sort_values("pagerank", ascending=ascending)
    
    def betweenness_centrality(self, k=1024, normalized=True, keep_attr=True, ascending=False):
        betweenness_df = cugraph.betweenness_centrality(self.G_cu, k=k, normalized=normalized)
        if keep_attr:
            self.nodes_df = self.nodes_df.merge(betweenness_df, left_on='node', right_on='vertex', how='left')
            self.nodes_df = self.nodes_df.drop(columns=['vertex'])
        return betweenness_df.sort_values("betweenness_centrality", ascending=ascending)
    
    def edge_betweenness_centrality(self, k=256, keep_attr=True, ascending=False):
        edge_betweenness_df = cugraph.edge_betweenness_centrality(self.G_cu, k=k)
        if keep_attr:
            self.edges_df = self.edges_df.merge(edge_betweenness_df, on=['src', 'dst'], how='left')
            self.edges_df.fillna(0, inplace=True)
        return edge_betweenness_df.sort_values("betweenness_centrality", ascending=ascending)
    
    def detect_communities(self):
        parts, _ = cugraph.louvain(self.G_cu)
        self.nodes_df = self.nodes_df.merge(parts, left_on='node', right_on='vertex', how='left')
        self.nodes_df = self.nodes_df.drop(columns=['vertex'])

    def filter_nodes(self, by: str = "pagerank", threshold: float = None, top_pct: float = None,
                 hybrid_attrs: list = None, hybrid_func=None, inplace=True):
        df = self.nodes_df.copy()
        
        if hybrid_attrs and hybrid_func:
            df['hybrid_metric'] = hybrid_func(*[df[col] for col in hybrid_attrs])
            by = 'hybrid_metric'

        if by not in df.columns:
            raise ValueError(f"Attribute '{by}' not found in nodes_df.")

        if threshold is not None:
            filtered_df = df[df[by] >= threshold]
        elif top_pct is not None:
            cutoff = int(len(df) * top_pct)
            filtered_df = df.nlargest(cutoff, columns=by)
        else:
            raise ValueError("Either `threshold` or `top_pct` must be specified.")

        if inplace:
            self.nodes_df = filtered_df.reset_index(drop=True)
            self.edges_df = self.edges_df[self.edges_df['src'].isin(self.nodes_df['node']) & self.edges_df['dst'].isin(self.nodes_df['node'])]
        return filtered_df.reset_index(drop=True).sort_values(by, ascending=True)
    
    def filter_edges(self, by: str = "betweenness_centrality", threshold: float = None, top_pct: float = None,
                 hybrid_attrs: list = None, hybrid_func=None, inplace=True):
        df = self.edges_df.copy()
        
        if hybrid_attrs and hybrid_func:
            df['hybrid_metric'] = hybrid_func(*[df[col] for col in hybrid_attrs])
            by = 'hybrid_metric'

        if by not in df.columns:
            raise ValueError(f"Attribute '{by}' not found in edges_df.")

        if threshold is not None:
            filtered_df = df[df[by] >= threshold]
        elif top_pct is not None:
            cutoff = int(len(df) * top_pct)
            filtered_df = df.nlargest(cutoff, columns=by)
        else:
            raise ValueError("Either `threshold` or `top_pct` must be specified.")

        if inplace:
            self.edges_df = filtered_df.reset_index(drop=True)
            self.nodes_df = self.nodes_df[self.nodes_df['node'].isin(
                    cudf.concat([self.edges_df['src'], self.edges_df['dst']])
                )].reset_index(drop=True)
        return filtered_df.reset_index(drop=True).sort_values(by, ascending=True)

    def remove_dead_ends_and_orphans(self, recurse=False, inplace=True):
        """
        Removes edges connected to orphan or dead-end nodes.
        If inplace=True, updates self.edges_df and self.nodes_df.
        """
        edges = self.edges_df.copy(deep=True)
        total_removed = 0

        while True:
            src_nodes = edges['src'].dropna().drop_duplicates()
            dst_nodes = edges['dst'].dropna().drop_duplicates()

            orphan_nodes = src_nodes[~src_nodes.isin(dst_nodes)]
            dead_end_nodes = dst_nodes[~dst_nodes.isin(src_nodes)]
            nodes_to_remove = cudf.concat([orphan_nodes, dead_end_nodes], ignore_index=True)

            if nodes_to_remove.empty:
                break

            before = len(edges)
            mask = ~edges['src'].isin(nodes_to_remove) & ~edges['dst'].isin(nodes_to_remove)
            edges = edges[mask]
            removed = before - len(edges)
            total_removed += removed

            if self.verbose:
                print(f"Removed {removed} edges...")

            if not recurse:
                break

        if self.verbose:
            print(f"Total edges removed: {total_removed}")

        if inplace:
            self.edges_df = edges.reset_index(drop=True)
            # Also filter nodes_df to keep only connected nodes
            connected_nodes = cudf.concat([edges['src'], edges['dst']]).drop_duplicates()
            self.nodes_df = self.nodes_df[self.nodes_df['node'].isin(connected_nodes)].reset_index(drop=True)
        else:
            # Also filter nodes_df to keep only connected nodes
            connected_nodes = cudf.concat([edges['src'], edges['dst']]).drop_duplicates()
            nodes = self.nodes_df[self.nodes_df['node'].isin(connected_nodes)].reset_index(drop=True)
            return edges.reset_index(drop=True), nodes


    def plot_node_attribute_distribution(self, attr: str = 'pagerank', hybrid_attrs: list = None, hybrid_func=None, bins: int = 30):
        """
        Plot histogram or bar chart depending on the type of node attribute.
        """

        if hybrid_attrs and hybrid_func:
            for attr in hybrid_attrs:
                if attr not in self.nodes_df.columns:
                    raise ValueError(f"Attribute '{attr}' not found in nodes_df.")
            self.nodes_df['hybrid_metric'] = hybrid_func(*[self.nodes_df[col] for col in hybrid_attrs])
            attr = 'hybrid_metric'
        else:
            if attr not in self.nodes_df.columns:
                raise ValueError(f"Attribute '{attr}' not found in nodes_df.")

        series = self.nodes_df[attr].to_pandas()

        plt.figure(figsize=(10, 6))
        if series.dtype == 'object' or series.nunique() < 20:
            # Categorical or few unique values -> bar plot
            sns.countplot(x=series)
            plt.xticks(rotation=45)
            plt.title(f"Distribution of {attr} (Categorical)")
        else:
            # Numeric -> histogram
            sns.histplot(series, bins=bins, kde=True)
            plt.title(f"Distribution of {attr} (Numeric)")

        plt.xlabel(attr)
        plt.ylabel("Count")
        plt.tight_layout()
        plt.show()


