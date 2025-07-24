from pydantic import BaseModel
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[ChatMessage] = []

class RAGChunk(BaseModel):
    content: str
    filename: str
    chunk_index: int

class RAGResponse(BaseModel):
    chunks: List[RAGChunk]
    query: str

class ChatResponse(BaseModel):
    message: str
    rag_used: bool = False
    rag_sources: Optional[List[RAGChunk]] = None