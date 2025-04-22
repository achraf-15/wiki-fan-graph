# 🏴‍☠️ One Piece Wiki Knowledge Graph

## 🧾 Project Overview

This project explores structured knowledge extraction and graph-based representation from a domain-specific corpus — specifically, the One Piece Wiki. It combines web crawling, text chunking, vector embedding, and graph construction to create a retrieval-friendly knowledge base that supports semantic search and large-scale visualization.

While this implementation focuses on the *One Piece* universe, the underlying pipeline is designed to be adaptable to any media content hosted on [fandom.com](https://www.fandom.com), given its standardized structure across wikis.

This project serves as a practical exploration of:  
- web crawling and parsing for structured data collection,  
- embedding and vector databases for RAG-like applications,  
- and building and visualizing large-scale knowledge graphs from fictional or domain-specific corpora.



---

## ✨ Features

- 🔍 **Recursive Wiki Crawler**  
  Automatically fetches and parses pages from the [One Piece Fandom Wiki](https://onepiece.fandom.com/wiki/One_Piece_Wiki), extracts text + metadata, and builds a local dataset.

- 🧩 **Chunk-based Text Structuring**  
  Pages are broken into meaningful content chunks (section-wise), each tracked with metadata and links to other pages.

- 🧠 **Text Embeddings + Vector DB**  
  Uses [Ollama](https://ollama.com/) to embed chunks and stores them with metadata in a [PostgreSQL](https://www.postgresql.org/) + [pgvector](https://github.com/pgvector/pgvector) database for similarity search.

- 🕸 **Knowledge Graph Builder**  
  Two graph views:
  - Page-level: one node per page.
  - Chunk-level: finer-grained view where edges are redirected to the top-k most similar chunks.

- ⚡ **GPU-Accelerated Visualization**  
  Uses [RAPIDS AI](https://rapids.ai/) (`cuDF`, `cuGraph`) and [Graphistry](https://www.graphistry.com/) to analyze and visualize massive graphs (30k+ nodes, 500k+ edges).

---

## 📁 Project Structure

```bash
project_root/
│
├── crawler/             # Web crawling, URL collection, HTML parsing
├── embedding/           # Embedding texts + saving to DB
├── knowledge_graph/     # Graph building + chunk-to-page linking
│
├── visualization.py     # cuDF/cuGraph tools + filtering, cleaning
├── example.ipynb        # Example: visualizing with Graphistry
├── database.py          # PostgreSQL/pgvector interface
├── config.py            # Constants, model config, DB path
├── main.py              # Pipeline launcher
└── README.md
```


## ⚙️ Installation

To run the project smoothly, you'll need to set up a few key components:

### 🐘 PostgreSQL + pgvector

Install PostgreSQL and the pgvector extension to store embeddings and metadata:

```bash
sudo apt install postgresql postgresql-contrib
sudo apt install postgresql-15-pgvector
```

Start the PostgreSQL server and set up the database:
```bash
sudo systemctl start postgresql
sudo -i -u postgres
psql
```
In the psql shell:
```sql
ALTER USER postgres WITH PASSWORD '0000';
CREATE DATABASE mydb;
\c mydb
CREATE EXTENSION IF NOT EXISTS vector;
```

More details ➤ https://github.com/pgvector/pgvector#installation

### 🤖 Ollama + Embedding Model

Install [Ollama](https://ollama.com/) to generate text embeddings:
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull nomic-embed-text
```

### ⚡ RAPIDS AI + Graphistry
This is optional but highly recommended for GPU-powered graph visualization and analysis.
```bash
conda create -n rapids-25.04 -c rapidsai -c conda-forge -c nvidia \
    cudf=25.04 cuml=25.04 cugraph=25.04 python=3.12 \
    'cuda-version>=12.0,<=12.8' graphistry networkx nx-cugraph=25.04
```

⚠️ You’ll need a CUDA-compatible GPU.
More details ➤ https://docs.rapids.ai/install and https://hub.graphistry.com/docs/

## 🚀 Usage

Once everything’s set up, you can run the full pipeline with:

BASH
python main.py
BASH

Or you can dive into individual parts if you're exploring or experimenting:

- Crawl One Piece Wiki pages and build the dataset:
  
  ```bash
  python crawler/crawler_pipeline.py
  ```

- Embed the textual chunks and store them with metadata:

  ```bash
  python embedding/embedding_main.py
  ```

- Build and refine the knowledge graph:

  ```bash
  python knowledge_graph/build.py
  ```

- Visualize your graph (optional but cool!):

  Open the `example.ipynb` notebook to interactively explore your graph using GPU acceleration via cuGraph and Graphistry.  
  *Note: You’ll need to [create a free Graphistry account](https://hub.graphistry.com/) and use your API key to enable visualizations.*


## 🌟 Features

- ⚓ Recursive crawler for structured web scraping of the One Piece Wiki.
- 📚 Text chunking with metadata and hyperlink graph extraction.
- 🧠 Ollama-powered embedding of all text data.
- 🗃️ PostgreSQL + pgvector integration for efficient similarity search.
- 🌐 Dynamic graph creation with both chunk-level and page-level resolution.
- 🚀 GPU-accelerated graph processing and filtering with RAPIDS AI.
- 🎇 Interactive graph visualization using Graphistry.

---

Navigating the seas of data, with a map to the Grand Line! 🏴‍☠️💻
