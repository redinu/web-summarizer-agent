"""
RAG (Retrieval-Augmented Generation) engine for Web Summarizer
Stores and retrieves summaries using vector embeddings
"""

import logging
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)


class RAGEngine:
    """RAG engine for storing and retrieving summaries"""

    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "web_summaries",
        embedding_model: str = "sentence-transformers",
        gemini_api_key: Optional[str] = None
    ):
        """
        Initialize RAG engine

        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the collection
            embedding_model: "sentence-transformers" (free) or "gemini" (requires API key)
            gemini_api_key: Google Gemini API key (required if using gemini embeddings)
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_model = embedding_model

        # Initialize ChromaDB client
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))

        # Choose embedding function
        if embedding_model == "gemini" and gemini_api_key:
            logger.info("Using Gemini embeddings")
            self.embedding_function = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
                api_key=gemini_api_key,
                model_name="models/embedding-001"
            )
        else:
            logger.info("Using Sentence Transformers embeddings (free)")
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )

        # Get or create collection
        try:
            self.collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"Loaded existing collection: {collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
                metadata={"description": "Web article summaries with embeddings"}
            )
            logger.info(f"Created new collection: {collection_name}")

    def store_summary(
        self,
        url: str,
        title: str,
        summary: str,
        key_points: List[str],
        category: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store a summary in the vector database

        Args:
            url: Source URL
            title: Article title
            summary: Summary text
            key_points: List of key points
            category: Article category
            metadata: Additional metadata

        Returns:
            Document ID
        """
        # Create unique ID from URL
        doc_id = f"doc_{hash(url)}"

        # Combine text for embedding
        combined_text = f"{title}\n\n{summary}\n\nKey Points:\n" + "\n".join(f"- {kp}" for kp in key_points)

        # Prepare metadata
        meta = {
            "url": url,
            "title": title,
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "key_points_count": len(key_points)
        }

        if metadata:
            meta.update(metadata)

        # Store in ChromaDB
        try:
            self.collection.add(
                documents=[combined_text],
                metadatas=[meta],
                ids=[doc_id]
            )
            logger.info(f"Stored summary for: {title}")
            return doc_id
        except Exception as e:
            logger.error(f"Failed to store summary: {e}")
            raise

    def search_similar(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar summaries

        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filters

        Returns:
            List of similar documents with metadata
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_metadata
            )

            # Format results
            formatted_results = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        "id": results['ids'][0][i],
                        "document": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i] if 'distances' in results else None
                    })

            logger.info(f"Found {len(formatted_results)} similar documents")
            return formatted_results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def generate_with_context(
        self,
        query: str,
        gemini_model,
        n_context_docs: int = 3
    ) -> Dict[str, Any]:
        """
        Generate response using RAG (retrieve + generate)

        Args:
            query: User query
            gemini_model: Initialized Gemini model
            n_context_docs: Number of context documents to retrieve

        Returns:
            Generated response with sources
        """
        # Retrieve relevant documents
        similar_docs = self.search_similar(query, n_results=n_context_docs)

        if not similar_docs:
            return {
                "answer": "No relevant documents found in the knowledge base.",
                "sources": [],
                "context_used": 0
            }

        # Build context from retrieved documents
        context_parts = []
        sources = []

        for i, doc in enumerate(similar_docs, 1):
            context_parts.append(f"[Source {i}]\n{doc['document']}\n")
            sources.append({
                "id": doc['id'],
                "title": doc['metadata'].get('title', 'Unknown'),
                "url": doc['metadata'].get('url', ''),
                "relevance_score": 1 - doc['distance'] if doc['distance'] else None
            })

        context = "\n".join(context_parts)

        # Generate response using Gemini
        prompt = f"""Based on the following context from our knowledge base, answer the question.

Context:
{context}

Question: {query}

Provide a comprehensive answer based on the context above. If the context doesn't fully answer the question, acknowledge that and provide what information is available."""

        try:
            response = gemini_model.generate_content(prompt)
            answer = response.text.strip()

            return {
                "answer": answer,
                "sources": sources,
                "context_used": len(similar_docs),
                "query": query
            }

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return {
                "answer": f"Error generating response: {str(e)}",
                "sources": sources,
                "context_used": 0
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection_name,
                "embedding_model": self.embedding_model,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}

    def delete_by_url(self, url: str) -> bool:
        """Delete a document by URL"""
        doc_id = f"doc_{hash(url)}"
        try:
            self.collection.delete(ids=[doc_id])
            logger.info(f"Deleted document: {url}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False

    def clear_all(self) -> bool:
        """Clear all documents from the collection"""
        try:
            # Delete and recreate collection
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            logger.info("Cleared all documents from collection")
            return True
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False
