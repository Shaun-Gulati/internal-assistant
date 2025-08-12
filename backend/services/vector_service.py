import os
import logging
import json
import numpy as np
import threading
from typing import List, Dict, Any
from services.llm_service import LLMService

logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self):
        try:
            self.llm_service = LLMService()
            # Check if LLM service is properly initialized
            if not self.llm_service.client:
                logger.warning("VectorService: LLM service not properly initialized - embeddings will not work")
        except Exception as e:
            logger.error(f"VectorService: Failed to initialize LLM service: {e}")
            self.llm_service = None
            
        self.vector_db_path = os.getenv('VECTOR_DB_PATH', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'embeddings'))
        
        # For MVP, we'll use a simple in-memory storage
        # In production, this would be replaced with FAISS or Chroma
        self.documents = []
        self.embeddings = []
        
        # Add lock for thread-safe operations
        self._save_lock = threading.Lock()
        
        self._load_documents()
    
    def search(self, query: str, user_role: str, limit: int = 5) -> List[Dict]:
        """Search for relevant documents based on query and user role."""
        try:
            # If LLM service is not available, return empty results
            if not self.llm_service or not self.llm_service.client:
                logger.warning("VectorService: Cannot perform search - LLM service not available")
                return []
            
            # Get query embedding
            query_embedding = self.llm_service.get_embeddings(query)
            if not query_embedding:
                logger.warning("VectorService: Failed to generate query embedding")
                return []
            
            # Calculate similarities
            similarities = []
            for i, doc_embedding in enumerate(self.embeddings):
                if doc_embedding:
                    similarity = self._cosine_similarity(query_embedding, doc_embedding)
                    similarities.append((similarity, i))
            
            # Sort by similarity and filter by role
            similarities.sort(reverse=True)
            
            # Filter documents by user role
            filtered_docs = []
            for similarity, doc_idx in similarities:
                doc = self.documents[doc_idx]
                if self._can_access_document(doc, user_role):
                    filtered_docs.append({
                        'content': doc['content'],
                        'source': doc['source'],
                        'metadata': doc['metadata'],
                        'similarity': similarity
                    })
                    if len(filtered_docs) >= limit:
                        break
            
            return filtered_docs
            
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return []
    
    def add_document(self, content: str, source: str, metadata: Dict, user_role: str = None):
        """Add a document to the vector database."""
        try:
            # If LLM service is not available, skip embedding generation
            if not self.llm_service or not self.llm_service.client:
                logger.warning("VectorService: Cannot add document - LLM service not available for embeddings")
                return False
            
            # Get embedding for the document
            embedding = self.llm_service.get_embeddings(content)
            if not embedding:
                logger.warning("VectorService: Failed to generate document embedding")
                return False
            
            # Create document entry
            document = {
                'content': content,
                'source': source,
                'metadata': metadata,
                'user_role': user_role
            }
            
            self.documents.append(document)
            self.embeddings.append(embedding)
            
            logger.info(f"Added document: {source} (total docs: {len(self.documents)})")
            
            # Save to disk for persistence
            self._save_documents()
            
            return True
            
        except Exception as e:
            logger.error(f"Add document error: {e}")
            return False
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0
            
            return dot_product / (norm1 * norm2)
            
        except Exception as e:
            logger.error(f"Cosine similarity error: {e}")
            return 0
    
    def _can_access_document(self, document: Dict, user_role: str) -> bool:
        """Check if user can access a document based on role-based filtering."""
        # Admin can access everything
        if user_role == 'admin':
            return True
        
        # Get document tags
        doc_tags = document.get('metadata', {}).get('tags', [])
        doc_source = document.get('source', '')
        
        # Role-based access rules
        role_access_rules = {
            'developer': ['github', 'slack-dev', 'slack-general', 'uploaded_document'],
            'marketing': ['slack-marketing', 'outlook', 'slack-general', 'uploaded_document'],
            'sales': ['slack-sales', 'outlook', 'slack-general', 'uploaded_document'],
            'user': ['slack-general', 'uploaded_document']  # Default access
        }
        
        allowed_sources = role_access_rules.get(user_role, ['slack-general'])
        
        # Check if document source is allowed for user role
        # For uploaded documents, check if the source starts with 'uploaded_document'
        if doc_source.startswith('uploaded_document'):
            return 'uploaded_document' in allowed_sources
        return doc_source in allowed_sources
    
    def _load_documents(self):
        """Load documents from disk."""
        try:
            docs_file = os.path.join(self.vector_db_path, 'documents.json')
            embeddings_file = os.path.join(self.vector_db_path, 'embeddings.json')
            
            if os.path.exists(docs_file):
                with open(docs_file, 'r') as f:
                    self.documents = json.load(f)
            
            if os.path.exists(embeddings_file):
                with open(embeddings_file, 'r') as f:
                    self.embeddings = json.load(f)
                    
        except Exception as e:
            logger.error(f"Load documents error: {e}")
            self.documents = []
            self.embeddings = []
    
    def _save_documents(self):
        """Save documents to disk."""
        with self._save_lock:
            try:
                logger.info(f"Saving documents to: {self.vector_db_path}")
                os.makedirs(self.vector_db_path, exist_ok=True)
                
                docs_file = os.path.join(self.vector_db_path, 'documents.json')
                embeddings_file = os.path.join(self.vector_db_path, 'embeddings.json')
                
                logger.info(f"Saving {len(self.documents)} documents to {docs_file}")
                with open(docs_file, 'w') as f:
                    json.dump(self.documents, f, indent=2)
                
                logger.info(f"Saving {len(self.embeddings)} embeddings to {embeddings_file}")
                with open(embeddings_file, 'w') as f:
                    json.dump(self.embeddings, f, indent=2)
                
                logger.info("Documents saved successfully")
                    
            except Exception as e:
                logger.error(f"Save documents error: {e}")
