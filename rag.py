import os
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from typing import List
from models import RAGChunk
from dotenv import load_dotenv

load_dotenv()

class RAGSystem:
    def __init__(self):
        self.chunk_size = int(os.getenv("CHUNK_SIZE", 1000))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 200))
        self.top_k = int(os.getenv("TOP_K_RESULTS", 5))
        
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="text-embedding-ada-002"
        )
        
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )
    
    def add_documents(self, documents_dir: str = "documents"):
        """Add all text documents from the documents directory to the vector store."""
        if not os.path.exists(documents_dir):
            print(f"Documents directory '{documents_dir}' not found")
            return
        
        # Clear existing documents
        self.collection.delete(where={})
        
        all_chunks = []
        all_metadatas = []
        all_ids = []
        
        for filename in os.listdir(documents_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(documents_dir, filename)
                
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                chunks = self.text_splitter.split_text(content)
                
                for i, chunk in enumerate(chunks):
                    all_chunks.append(chunk)
                    all_metadatas.append({
                        "filename": filename,
                        "chunk_index": i
                    })
                    all_ids.append(f"{filename}_{i}")
        
        if all_chunks:
            # Generate embeddings
            embeddings = self.embeddings.embed_documents(all_chunks)
            
            # Add to ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=all_chunks,
                metadatas=all_metadatas,
                ids=all_ids
            )
            
            print(f"Added {len(all_chunks)} chunks from {len(set(m['filename'] for m in all_metadatas))} documents")
    
    def query(self, query: str, top_k: int = None) -> List[RAGChunk]:
        """Query the vector store and return relevant chunks."""
        if top_k is None:
            top_k = self.top_k
        
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        chunks = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i]
                chunks.append(RAGChunk(
                    content=doc,
                    filename=metadata['filename'],
                    chunk_index=metadata['chunk_index']
                ))
        
        return chunks

# Global RAG instance
rag_system = RAGSystem()