# embedding/model.py

import numpy as np
import ollama

class OllamaEmbedding:
    def __init__(self, model="nomic-embed-text"):
        self.model = model

    def encode(self, texts):
        result = ollama.embed(model=self.model, input=texts)
        return np.array(result["embeddings"])
    


def process_batch(batch_data, embedding_model):
    texts = [chunk['text'] for chunk in batch_data]
    embeddings = embedding_model.encode(texts)

    return [
        {
            'chunk_id': chunk['chunk_id'],
            'url': chunk['url'],
            'title': chunk['title'],
            'section': chunk['section'],
            'category': chunk['category'],
            'text': chunk['text'],
            'embedding': embedding
        }
        for chunk, embedding in zip(batch_data, embeddings)
    ]

#import torch 
#from transformers import AutoTokenizer
#from sentence_transformers import SentenceTransformer 
#from openai import OpenAI
# 
#   
# class vllmEmbedding:
#     def __init__(self, base_url="http://localhost:8000/v1"):
#         self.client = OpenAI(base_url=base_url, api_key="not-needed")

#     def encode(self, texts):
#         result = self.client.embeddings.create(
#                                 model="BAAI/bge-base-en-v1.5",
#                                 input=texts
#                             )
#         embeddings = [e.embedding for e in result.data]
#         return np.array(embeddings)
 

# class HuggingFaceEmbedding:
#     def __init__(self, model_name="BAAI/bge-large-en-v1.5", fp16=False):
#         self.model_name = model_name
#         self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
#         self.model = SentenceTransformer(self.model_name, device=self.device, trust_remote_code=True)

#         if fp16:
#             self.model._first_module().auto_model.half()
            

#     def encode(self, texts, batch_size):
#         embeddings = self.model.encode(texts, convert_to_numpy=True, batch_size=batch_size, show_progress_bar=False)
#         return embeddings


# class TextChunker:
#     def __init__(self, model, max_tokens, overlap, p = 0.6):
#         self.model = model 
#         self.max_tokens = int(max_tokens * p)
#         self.overlap = overlap
#         self.tokenizer = AutoTokenizer.from_pretrained(self.model)

#     def chunk_text(self, text):
#         tokens = self.tokenizer.encode(text, add_special_tokens=False)
#         chunks = []
#         start = 0
#         while start < len(tokens):
#             end = start + self.max_tokens
#             chunk = tokens[start:end]
#             chunks.append(self.tokenizer.decode(chunk))
#             start += self.max_tokens - self.overlap
#         return chunks
    
#     def preprocess_texts(self, chunks):
#         prep_texts= []
#         for chunk in chunks:
#             sub_texts = self.chunk_text(chunk['text'])
#             prep_texts.extend(
#                         [
#                     {
#                         'chunk_id': chunk['chunk_id']+'_'+str(i),
#                         'url': chunk['url'],
#                         'title': chunk['title'],
#                         'section': chunk['section'],
#                         'text': sub_text,
#                     }   
#                      for i, sub_text in enumerate(sub_texts)
#                 ]
#             )
#         return prep_texts
    
#     def get_indices(self, chunks):
#         chunk2subs = {}
#         for chunk in chunks:
#             chunk2subs[chunk['chunk_id']] = []
#             for i in range(len(self.chunk_text(chunk['text']))): 
#                 chunk2subs[chunk['chunk_id']].append(chunk['chunk_id']+'_'+str(i))
#         return chunk2subs
    
#     def save_indices(self, chunks, outdir="data"):
#         os.makedirs(outdir, exist_ok=True)
#         filename = "chunk_subs.json"
#         file_path = os.path.join(outdir, filename)
        
#         chunk2subs = self.get_indices(chunks)
#         with open(file_path, "w", encoding="utf-8") as f:
#             json.dump(chunk2subs, f, indent=2, ensure_ascii=False)