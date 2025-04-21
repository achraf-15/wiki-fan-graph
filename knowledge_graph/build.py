from knowledge_graph.knowledge_graph import KnowledgeGraph
from database import EmbeddingDatabase
from config import METADATA_DIR, GRAPH_DIR, DOC_DIR, DATA_DIR


def build_main(top_k=3,save_to_local=True, from_local=False, verbose=1):
    # Setup
    kg = KnowledgeGraph(data_dir=DATA_DIR, metadata_dir=METADATA_DIR, page_dir=DOC_DIR, graph_dir=GRAPH_DIR, EmbeddingDatabase=EmbeddingDatabase, verbose=verbose)

    if from_local:
        if verbose:
            print("Loading Knowledge Graph from disk...")
        kg.load(DATA_DIR, graph_type='chunk')
        kg.load(DATA_DIR, graph_type='page')

        if verbose >= 2:
            print("-----"*10)
            print("Chunk Knowledge Graph Nodes: ",len(kg.chunk_graph.nodes))
            print("Chunk Knowledge Graph Edges: ",len(kg.chunk_graph.edges))
            print("-----"*10)
            print("Page Knowledge Graph Nodes: ",len(kg.page_graph.nodes))
            print("Page Knowledge Graph Edges: ",len(kg.page_graph.edges))
            print("-----"*10)
        

        kg.db.close_connection()


    else:
        # Step 1: Build the raw graph
        if verbose:
            print("Setting up Knowledge Graph...")
        kg.setup()                      
        if verbose >= 2:
            print("Knowledge Graph Nodes: ",len(kg.graph.nodes))
            print("Knowledge Graph Edges: ",len(kg.graph.edges))
            print("-----"*10)

        # Step 2: Connect relevant chunks
        if verbose:
            print("Building Chunk and Page Knowledge Graph...")
        kg.build(top_k=top_k)    
        if verbose >= 2:
            print("Chunk Knowledge Graph Nodes: ",len(kg.chunk_graph.nodes))
            print("Chunk Knowledge Graph Edges: ",len(kg.chunk_graph.edges))
            print("-----"*10)
            print("Page Knowledge Graph Nodes: ",len(kg.page_graph.nodes))
            print("Page Knowledge Graph Edges: ",len(kg.page_graph.edges))
            print("-----"*10)

        if save_to_local:
            kg.save(DATA_DIR, graph_type='chunk')
            kg.save(DATA_DIR, graph_type='page')
        if verbose >= 2:
            print("-----"*10)  

        kg.db.close_connection()


    


