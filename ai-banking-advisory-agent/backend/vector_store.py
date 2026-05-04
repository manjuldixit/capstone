"""
Vector Store Setup for Phase 4: Chroma-based Retrieval
Manages embedding, storage, and retrieval from vector database
"""

import json
import logging
from typing import List, Dict, Any, Tuple
from pathlib import Path
import os

logger = logging.getLogger(__name__)

try:
    import chromadb
except ImportError:
    logger.warning("chromadb not installed. Run: pip install chromadb sentence-transformers")
    chromadb = None

from document_processor import DocumentProcessor, Document

CHROMADB_AVAILABLE = chromadb is not None


class NoOpVectorStore:
    """Fallback vector store when chromadb is unavailable."""

    def __init__(self, *args, **kwargs):
        self.db_path = None
        self.collection_name = kwargs.get('collection_name', 'equipment_financing')
        self.embedding_model = None
        self.retrieval_stats = {
            "total_queries": 0,
            "avg_results": 0,
            "total_results": 0
        }
        logger.warning("Using NoOpVectorStore because chromadb is unavailable.")

    def add_documents(self, documents, force_reinit=False):
        logger.warning("Skipping document indexing because chromadb is unavailable.")
        return 0

    def retrieve(self, query: str, top_k: int = 3):
        self.retrieval_stats["total_queries"] += 1
        return []

    def get_collection_stats(self):
        return {
            "collection_name": self.collection_name,
            "document_count": 0,
            "embedding_model": self.embedding_model,
            "retrieval_stats": self.retrieval_stats
        }


class VectorStore:
    """
    Manages Chroma vector store for equipment financing documents.
    
    Features:
    - Initialize/load vector database
    - Add documents with embeddings
    - Retrieve similar documents by semantic search
    - Track retrieval statistics
    """
    
    def __init__(
        self,
        db_path: str = "data/chroma_db",
        collection_name: str = "equipment_financing",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize vector store.
        
        Args:
            db_path: Path to Chroma database directory
            collection_name: Name of collection within database
            embedding_model: Sentence-transformers model name
        """
        if chromadb is None:
            raise RuntimeError("chromadb is required for VectorStore")

        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        
        # Initialize Chroma client (new API)
        self.client = chromadb.PersistentClient(path=str(self.db_path))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        self.retrieval_stats = {
            "total_queries": 0,
            "avg_results": 0,
            "total_results": 0
        }
        
        logger.info(f"Initialized VectorStore at {self.db_path}")
    
    def add_documents(self, documents: List[Document], force_reinit: bool = False) -> int:
        """
        Add documents to vector store with embeddings.
        
        Args:
            documents: List of Document objects to add
            force_reinit: If True, clear collection and re-add all
        
        Returns:
            Number of documents added
        """
        if force_reinit:
            # For force reinit, delete and recreate collection
            try:
                self.client.delete_collection(name=self.collection_name)
                self.collection = self.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info("Cleared collection for re-initialization")
            except Exception as e:
                logger.warning(f"Could not delete collection: {e}")
        
        # Prepare data for Chroma
        ids = []
        documents_text = []
        metadatas = []
        
        for doc in documents:
            ids.append(doc.doc_id)
            documents_text.append(doc.content)
            metadatas.append(doc.metadata)
        
        # Add to collection (Chroma handles embedding internally)
        self.collection.add(
            ids=ids,
            documents=documents_text,
            metadatas=metadatas
        )
        
        logger.info(f"Added {len(documents)} documents to vector store")
        return len(documents)
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: User query string
            top_k: Number of top results to return
        
        Returns:
            List of retrieved documents with relevance scores
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Transform results to readable format
            retrieved = []
            if results and results["documents"]:
                for i, (doc, metadata, distance) in enumerate(
                    zip(
                        results["documents"][0],
                        results["metadatas"][0],
                        results["distances"][0]
                    )
                ):
                    # Chroma returns distance; convert to similarity (lower distance = higher similarity)
                    similarity = 1 - (distance / 2)  # Normalize for cosine distance
                    
                    retrieved.append({
                        "rank": i + 1,
                        "content": doc,
                        "metadata": metadata,
                        "similarity_score": round(similarity, 3),
                        "distance": round(distance, 3)
                    })
            
            # Update stats
            self.retrieval_stats["total_queries"] += 1
            self.retrieval_stats["total_results"] += len(retrieved)
            self.retrieval_stats["avg_results"] = (
                self.retrieval_stats["total_results"] / self.retrieval_stats["total_queries"]
            )
            
            logger.debug(f"Retrieved {len(retrieved)} documents for query: {query[:50]}...")
            return retrieved
        
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        document_count = 0
        try:
            if hasattr(self.collection, "get"):
                document_count = len(self.collection.get()["ids"])
            elif hasattr(self.collection, "count"):
                document_count = self.collection.count()
        except Exception:
            document_count = 0

        return {
            "collection_name": self.collection_name,
            "document_count": document_count,
            "embedding_model": self.embedding_model,
            "retrieval_stats": self.retrieval_stats
        }
    
    def export_stats(self, output_path: str) -> None:
        """Export collection statistics"""
        stats = self.get_collection_stats()
        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=2)
        logger.info(f"Exported stats to {output_path}")


class RetrieverManager:
    """
    High-level manager for document processing and retrieval setup.
    Orchestrates document processor and vector store.
    """
    
    def __init__(
        self,
        kb_path: str,
        db_path: str = "data/chroma_db",
        collection_name: str = "equipment_financing"
    ):
        """Initialize retriever manager"""
        self.kb_path = kb_path
        self.db_path = db_path
        self.collection_name = collection_name
        
        self.processor = DocumentProcessor(kb_path)
        try:
            self.vector_store = VectorStore(db_path, collection_name)
        except Exception as exc:
            logger.warning(f"VectorStore initialization failed: {exc}")
            self.vector_store = NoOpVectorStore(collection_name=collection_name)
    
    def setup(self, force_reinit: bool = False) -> int:
        """
        Full setup: process documents and add to vector store.
        
        Args:
            force_reinit: Clear and rebuild vector store
        
        Returns:
            Number of documents processed
        """
        logger.info("Starting RetrieverManager setup...")
        
        # Process documents
        documents = self.processor.process()
        logger.info(f"Processed {len(documents)} documents")
        
        # Export processed documents for inspection
        docs_export_path = Path(self.db_path).parent / "processed_documents.json" if self.db_path else Path("processed_documents.json")
        self.processor.export_documents(str(docs_export_path))

        # Add to vector store if available
        added = self.vector_store.add_documents(documents, force_reinit=force_reinit)
        return added
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Run a retrieval query through the configured vector store"""
        return self.vector_store.retrieve(query, top_k)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics"""
        return self.vector_store.get_collection_stats()


def initialize_retriever(
    kb_path: str = "data/knowledge_base.json",
    db_path: str = "data/chroma_db",
    force_reinit: bool = False
) -> RetrieverManager:
    """
    Convenience function to initialize retriever.
    
    Args:
        kb_path: Path to knowledge base JSON
        db_path: Path to Chroma database
        force_reinit: Rebuild vector store
    
    Returns:
        Initialized RetrieverManager
    """
    manager = RetrieverManager(kb_path, db_path)
    manager.setup(force_reinit=force_reinit)
    return manager


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)
    
    # Initialize
    manager = initialize_retriever(force_reinit=True)
    
    # Test retrieval
    test_queries = [
        "What are the rates for commercial equipment?",
        "What credit score do I need?",
        "How long is the application process?"
    ]
    
    for query in test_queries:
        print(f"\n\nQuery: {query}")
        results = manager.retrieve(query, top_k=2)
        for result in results:
            print(f"\nRank {result['rank']} (similarity: {result['similarity_score']})")
            print(f"Content: {result['content'][:300]}...")
    
    print("\n\nCollection Stats:")
    import pprint
    pprint.pprint(manager.get_stats())
