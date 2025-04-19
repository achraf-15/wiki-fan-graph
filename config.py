# config.py

BASE_URL = 'https://onepiece.fandom.com'
WIKI_URL = 'https://onepiece.fandom.com/wiki/'

DATA_DIR = "data/"

METADATA_DIR = f"{DATA_DIR}/metadata/"
DOC_DIR = f"{DATA_DIR}/pages/"
GRAPH_DIR = f"{DATA_DIR}/graph/"
KG_DIR = f"{DATA_DIR}/knowledge_graph/"

DB_CONFIG = {
    "host": "localhost", 
    "port": "5432",
    "database": "mydb",
    "user": "postgres",
    "password": "0000"
}

EMBEDDING_DIM = 768
MAX_TOKENS = 8192
MODEL_NAME = "nomic-ai/nomic-embed-text-v1"
