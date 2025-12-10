import chromadb
from typing import List, Dict, Any
from app.core.config import settings

class VectorStore:
    """Interface with ChromaDB for storing and retrieving document embeddings"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMADB_PATH)
        self.collection = None
    
    def create_collection(self, name: str = "documents"):
        """Create or get a collection in ChromaDB"""
        try:
            self.collection = self.client.create_collection(name=name)
        except Exception:
            # Collection already exists, get it
            self.collection = self.client.get_collection(name=name)
    
    def add_documents(self, ids: List[str], embeddings: List[List[float]], 
                     metadatas: List[Dict[str, Any]], documents: List[str]):
        """Add documents to the vector store"""
        if not self.collection:
            self.create_collection()
            
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
    
    def search(self, query_embedding: List[float], n_results: int = 5) -> Dict[str, Any]:
        """Search for similar documents"""
        if not self.collection:
            self.create_collection()
            
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return results
    
    def delete_collection(self, name: str = "documents"):
        """Delete a collection"""
        try:
            self.client.delete_collection(name=name)
        except Exception:
            pass  # Collection doesn't exist