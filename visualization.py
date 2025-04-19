import os
import json
import networkx as nx
from networkx.readwrite import json_graph
from config import DATA_DIR

def load(outdir: str, graph_type: str = 'chunk',verbose=1):
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
        graph = json_graph.node_link_graph(data)
    elif graph_type == 'page':
        graph = json_graph.node_link_graph(data)
    else:
        raise ValueError("graph_type must be 'chunk' or 'page'")  
    
    if verbose:
        print(f"Graph loaded from {file_path}")

    return graph


import cudf
import cugraph

# Convert NetworkX DiGraph to cuGraph format
def nx_to_cugraph(G):
    edges = nx.to_pandas_edgelist(G)
    gdf_edges = cudf.DataFrame.from_pandas(edges)
    # Rename for cuGraph convention
    gdf_edges = gdf_edges.rename(columns={'source': 'src', 'target': 'dst'})
    return gdf_edges

def remove_dead_ends_and_orphans(edges_df, recurse=False):
    """
    Removes orphan (in-degree = 0) and dead-end (out-degree = 0) nodes from a DiGraph.
    """
    while True:
        in_deg = edges_df.groupby('dst').size().reset_index(name='in_deg')
        out_deg = edges_df.groupby('src').size().reset_index(name='out_deg')

        all_nodes = cudf.concat([in_deg.rename(columns={'dst': 'node'}), 
                                 out_deg.rename(columns={'src': 'node'})], ignore_index=True)
        degrees = all_nodes.groupby('node').sum().reset_index()

        good_nodes = degrees[(degrees['in_deg'] > 0) & (degrees['out_deg'] > 0)]['node']
        new_edges = edges_df[edges_df['src'].isin(good_nodes) & edges_df['dst'].isin(good_nodes)]

        if len(new_edges) == len(edges_df) or not recurse:
            break
        edges_df = new_edges

    return edges_df


def compute_centralities(G_df):
    """
    Computes PageRank, Betweenness Centrality (nodes), and Edge Betweenness.
    Returns 3 dataframes.
    """
    G_cu = cugraph.Graph()
    G_cu.from_cudf_edgelist(G_df, source='src', destination='dst', edge_attr='weight', renumber=True)

    pagerank_df = cugraph.pagerank(G_cu)
    betweenness_df = cugraph.betweenness_centrality(G_cu)
    edge_betweenness_df = cugraph.edge_betweenness_centrality(G_cu)
    
    return pagerank_df, betweenness_df, edge_betweenness_df

def compute_louvain_communities(G_df):
    """
    Runs Louvain clustering on undirected version of G.
    Returns {node: community_id}
    """
    G_cu = cugraph.Graph()
    G_cu.from_cudf_edgelist(G_df, source='src', destination='dst', edge_attr='weight', renumber=True)
    parts, _ = cugraph.louvain(G_cu)
    return parts

def filter_nodes_by_hybrid_score(pagerank_df, betweenness_df, p=0.8):
    """
    Combines PageRank and Betweenness into a hybrid score, keeps top-K nodes.
    """
    merged = pagerank_df.merge(betweenness_df, on='vertex', suffixes=('_pr', '_bc'))
    merged['hybrid'] = merged['pagerank_pr'] * merged['betweenness_bc']
    top_k = int(len(merged) * p)
    top_nodes = merged.nlargest(top_k, 'hybrid')['vertex']
    return top_nodes

def filter_edges_by_edge_betweenness(edges_df, edge_betweenness_df, min_score=0.001):
    """
    Removes edges below edge betweenness threshold.
    """
    filtered = edges_df.merge(edge_betweenness_df, on=['src', 'dst'])
    filtered = filtered[filtered['betweenness_centrality'] >= min_score]
    return filtered



G = load(DATA_DIR,'chunk')
print("Chunk Knowledge Graph Nodes: ",len(G.nodes))
print("Chunk Knowledge Graph Edges: ",len(G.edges))

edges_df = nx_to_cugraph(G)
print(edges_df.head())

pagerank_df, betweenness_df, edge_betweenness_df = compute_centralities(edges_df)
communities = compute_louvain_communities(edges_df)
edges_df = filter_nodes_by_hybrid_score(pagerank_df, betweenness_df, p=0.8)
edges_df = remove_dead_ends_and_orphans(edges_df, recurse=False)
edges_df = filter_edges_by_edge_betweenness(edges_df, edge_betweenness_df, min_score=0.001)

nodes_df = cudf.concat([
        edges_df['src'], edges_df['dst']
    ]).drop_duplicates().reset_index(drop=True).to_frame(name='node')

nodes_df = nodes_df.merge(louvain_df, left_on='node', right_on='vertex', how='left')
nodes_df = nodes_df.drop(columns=['vertex'])


graphistry.register( 
        api=3,
        personal_key_id=personal_key_id,
        personal_key_secret=personal_key_secret
    )

g = graphistry.edges(edges_df, 'src', 'dst')
g = g.nodes(nodes_df, 'node')
g = g.bind(point_title='node') 
g = g.modularity_weighted_layout("partition")

g.plot()