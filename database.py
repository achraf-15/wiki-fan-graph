# database.py

import psycopg2
from psycopg2.extras import execute_values, execute_batch
from pgvector.psycopg2 import register_vector
from config import DB_CONFIG, EMBEDDING_DIM

import pandas as pd
import pandas.io.sql as sqlio

class EmbeddingDatabase:

    columns = ['id', 'chunk_id', 'url', 'title', 'section', 'text', 'embedding']

    def __init__(self):
        self.conn = self.connect_db()
        register_vector(self.conn)

    def connect_db(self):
        """Establish a connection to the PostgreSQL database."""
        return psycopg2.connect(**DB_CONFIG)

    def create_embeddings_table(self):
        """Create the embeddings table if it does not exist."""
        with self.conn.cursor() as cur:
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS embeddings (
                    id SERIAL PRIMARY KEY,
                    chunk_id TEXT UNIQUE,
                    url TEXT,
                    title TEXT,
                    category TEXT,
                    section TEXT,
                    text TEXT,
                    embedding vector({EMBEDDING_DIM})
                );
            """)
            self.conn.commit()

    def delete_embeddings_table(self):
        """Drop the embeddings table if it exists."""
        with self.conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS embeddings;")
            self.conn.commit()

    def to_pandas(self):
        with self.conn.cursor() as cur:
            cur.execute(
                    "SELECT chunk_id, title, embedding FROM embeddings",
                )
            tuples_list  = cur.fetchall()
        df = pd.DataFrame(tuples_list, columns=["chunk_id", "title", "embedding"])
        return df


    def insert_embeddings(self, data, page_size):
        """Insert embeddings data into the embeddings table."""
        with self.conn.cursor() as cur:
            rows = [
                (doc['chunk_id'], doc['url'], doc['title'], doc['category'], doc['section'], doc['text'], doc['embedding'])
                for doc in data if doc['embedding'].any()
            ]
            execute_batch(cur, """
                INSERT INTO embeddings (chunk_id, url, title, category, section, text, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (chunk_id) DO NOTHING;
            """, rows, page_size=page_size)
            self.conn.commit()

    def dense_search(self,subset, embedding, topk):
        with self.conn.cursor() as cur:
            cur.execute(
                        """
                    SELECT chunk_id, embedding  <#> %s::vector AS similarity
                    FROM embeddings
                    WHERE chunk_id = ANY(%s)
                    ORDER BY similarity
                    LIMIT %s
                    """,
                    (embedding, list(subset), topk)
                    )
            top_chunks = cur.fetchall()
        return [(chunk_id, -similarity) for chunk_id, similarity in top_chunks] if top_chunks else None
    
    def get_embedding(self, chunk_id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT embedding FROM embeddings WHERE chunk_id = %s", (chunk_id,))
            result = cur.fetchone()
        return result[0] if result else None
    
    def get_text(self, chunk_id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT text FROM embeddings WHERE chunk_id = %s", (chunk_id,))
            result = cur.fetchone()
        return result[0] if result else None
    
    def filter_by_title(self, title):
        with self.conn.cursor() as cur:
            cur.execute("SELECT chunk_id FROM embeddings WHERE title = %s", (title,))
            result = cur.fetchall()
        return result

    def check_embeddings_table(self):
        """Check the number of records in the embeddings table."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as cnt FROM embeddings;")
            num_records = cur.fetchone()[0]
            print("Number of vector records in embeddings:", num_records)

    def close_connection(self):
        """Close the database connection."""
        self.conn.close()
