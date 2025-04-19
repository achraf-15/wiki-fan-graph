# crawler/models/schemas.py
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class ChunkData:
    url: str
    chunk_id: str
    title: str
    category: str
    text: str
    section: str
    links: List[Tuple[str, str]]
    token_count: int = 0

@dataclass
class DocumentData:
    url: str
    title: str
    category: str
    text: str
    links: List[Tuple[str, str]]