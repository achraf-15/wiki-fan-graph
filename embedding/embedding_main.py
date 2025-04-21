# main.py

from config import METADATA_DIR, MODEL_NAME, MAX_TOKENS
from database import EmbeddingDatabase
#from embedding.model import HuggingFaceEmbedding, TextChunker,  process_batch , OllamaEmbedding #, vllmEmbedding
from embedding.model import OllamaEmbedding, process_batch
from embedding.dataloader import load_all_chunks, batch_chunks

from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np

#from transformers import AutoTokenizer


def embedding_main(batch_size = 64, reset_table = True, verbose=1):

    model = OllamaEmbedding()
    #model = vllmEmbedding(base_url="http://localhost:8000/v1")
    #model = HuggingFaceEmbedding(model_name=MODEL_NAME, fp16=True)
    #chunker = TextChunker(model=MODEL_NAME, max_tokens=MAX_TOKENS, overlap=64)

    if verbose:
        print("Loading and Preprocessing texts...")
    # Load + preprocess 
    all_chunks = load_all_chunks(METADATA_DIR)
    all_chunks = all_chunks[:150]
    #all_chunks = chunker.preprocess_texts(all_chunks)
    #chunker.save_indices(all_chunks)

    if verbose:
        print("Total Number of Chunks : ", len(all_chunks))

    post_processed_data = [] 
    for batch in tqdm(batch_chunks(all_chunks, batch_size), total=len(all_chunks)//batch_size, desc="Embedding Chunks...",disable=(verbose<1)):
        batch_data = process_batch(batch, model, batch_size)
        post_processed_data.extend(batch_data)

     # Setup
    if verbose:
        print("Connecting to PostgresSQL Database...")
    db = EmbeddingDatabase()

    if reset_table:
        db.delete_embeddings_table()
        if verbose >= 2:
            print("Table Deleted!")
        db.create_embeddings_table()
        if verbose >= 2:
            print("Table Created Successfully!")
            print("-----"*10)
        


    db.insert_embeddings(post_processed_data, page_size=1000)
    
    db.check_embeddings_table()
    db.close_connection()

    if verbose:
        print("Embedding pipeline finished.")
    if verbose >= 2:
        print("-----"*10)

