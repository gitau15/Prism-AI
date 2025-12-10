from app.utils.document_parser import parse_document
from app.utils.document_chunker import chunk_document
from app.utils.embedder import Embedder
from app.utils.vector_store import VectorStore
from app.utils.llm_client import LLMClient
from typing import List, Dict, Any

class ProcessingPipeline:
    """Orchestrate the entire document processing and querying pipeline"""
    
    def __init__(self):
        self.embedder = Embedder()
        self.vector_store = VectorStore()
        self.llm_client = LLMClient()
    
    def process_document(self, file_path: str, file_type: str, document_id: int) -> Dict[str, Any]:
        """Process a document through the full ingestion pipeline"""
        # Step 1: Parse the document
        print(f"Parsing document {document_id}...")
        text_content = parse_document(file_path, file_type)
        
        # Step 2: Chunk the document
        print("Chunking document...")
        chunks = chunk_document(text_content, method="paragraph")
        
        # Step 3: Generate embeddings
        print("Generating embeddings...")
        embeddings = self.embedder.embed_batch(chunks)
        
        # Step 4: Store in vector database
        print("Storing in vector database...")
        metadatas = [{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))]
        ids = [f"{document_id}_{i}" for i in range(len(chunks))]
        
        self.vector_store.add_documents(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=chunks
        )
        
        return {
            "status": "success",
            "document_id": document_id,
            "chunks_processed": len(chunks)
        }
    
    def query_documents(self, query: str, user_id: int) -> Dict[str, Any]:
        """Process a user query through the RAG pipeline"""
        # Step 1: Generate query embedding
        print("Generating query embedding...")
        query_embedding = self.embedder.embed_text(query)
        
        # Step 2: Search vector database
        print("Searching for relevant documents...")
        search_results = self.vector_store.search(query_embedding, n_results=3)
        
        # Step 3: Extract relevant context
        relevant_context = "\n".join(search_results['documents'][0]) if search_results['documents'] else ""
        
        # Step 4: Format prompt
        print("Formatting prompt...")
        prompt = self.llm_client.format_prompt(query, relevant_context)
        
        # Step 5: Generate response
        print("Generating response...")
        response = self.llm_client.generate_response(prompt)
        
        # Step 6: Return formatted response
        return {
            "response": response,
            "sources": search_results['ids'][0] if search_results['ids'] else []
        }