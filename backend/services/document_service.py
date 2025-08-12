import os
import logging
import PyPDF2
from docx import Document
from typing import List, Dict, Any
from services.vector_service import VectorService

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self):
        self.vector_service = VectorService()
        self.upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        
        # Create upload directory if it doesn't exist
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
    
    def check_duplicate_file(self, filename: str, user_role: str = None) -> bool:
        """Check if a file with the same name already exists."""
        try:
            if not self.vector_service:
                return False
            
            # Check if document with same filename exists
            for doc in self.vector_service.documents:
                if doc.get('source', '').startswith(f'uploaded_document_{filename}'):
                    # Check access permissions
                    if user_role is None or self.vector_service._can_access_document(doc, user_role):
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Check duplicate file error: {e}")
            return False
    
    def replace_document(self, filename: str, user_role: str = None) -> Dict[str, Any]:
        """Delete existing document and return success status."""
        try:
            # Delete the existing document first
            delete_result = self.delete_document(filename, user_role)
            if delete_result['success']:
                logger.info(f"Replaced existing document: {filename}")
                return {'success': True, 'filename': filename, 'replaced': True}
            else:
                return {'success': False, 'error': f'Failed to replace document: {delete_result["error"]}'}
                
        except Exception as e:
            logger.error(f"Replace document error: {e}")
            return {'success': False, 'error': f'Failed to replace document: {str(e)}'}

    def process_document(self, file_path: str, filename: str, user_role: str = None, replace_existing: bool = False) -> Dict[str, Any]:
        """Process a document file and add it to the vector database."""
        try:
            # Check for duplicate file
            is_duplicate = self.check_duplicate_file(filename, user_role)
            
            if is_duplicate and not replace_existing:
                return {
                    'success': False,
                    'error': 'File already exists',
                    'duplicate': True,
                    'filename': filename
                }
            
            # If duplicate and replace is requested, delete existing first
            if is_duplicate and replace_existing:
                replace_result = self.replace_document(filename, user_role)
                if not replace_result['success']:
                    return replace_result
            
            # Determine file type and extract text
            file_extension = filename.lower().split('.')[-1]
            
            if file_extension == 'pdf':
                text_content = self._extract_pdf_text(file_path)
            elif file_extension in ['docx', 'doc']:
                text_content = self._extract_docx_text(file_path)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported file type: {file_extension}. Supported types: PDF, DOCX, DOC'
                }
            
            if not text_content.strip():
                return {
                    'success': False,
                    'error': 'No text content found in the document'
                }
            
            # Split text into chunks for better processing
            chunks = self._chunk_text(text_content)
            
            # Add each chunk to the vector database
            added_chunks = 0
            from datetime import datetime
            upload_time = datetime.now().isoformat()
            
            for i, chunk in enumerate(chunks):
                metadata = {
                    'filename': filename,
                    'file_type': file_extension,
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'source': 'uploaded_document',
                    'tags': ['document', file_extension],
                    'uploaded_at': upload_time
                }
                
                success = self.vector_service.add_document(
                    content=chunk,
                    source=f'uploaded_document_{filename}',
                    metadata=metadata,
                    user_role=user_role
                )
                
                if success:
                    added_chunks += 1
                else:
                    logger.error(f"Failed to add chunk {i} for document {filename}")
            
            return {
                'success': True,
                'filename': filename,
                'chunks_added': added_chunks,
                'total_chunks': len(chunks),
                'file_size': os.path.getsize(file_path),
                'replaced': is_duplicate and replace_existing
            }
            
        except Exception as e:
            logger.error(f"Document processing error: {e}")
            return {
                'success': False,
                'error': f'Failed to process document: {str(e)}'
            }
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from a PDF file."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                return text
                
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from a DOCX file."""
        try:
            doc = Document(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text
            
        except Exception as e:
            logger.error(f"DOCX extraction error: {e}")
            raise Exception(f"Failed to extract text from DOCX: {str(e)}")
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks for better processing."""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at a sentence boundary
            if end < len(text):
                # Look for sentence endings
                for i in range(end, max(start + chunk_size - 100, start), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def get_uploaded_documents(self, user_role: str = None) -> List[Dict[str, Any]]:
        """Get list of uploaded documents accessible to the user."""
        try:
            documents = {}
            
            # Get documents from vector service
            if self.vector_service:
                all_docs = self.vector_service.documents
                
                for doc in all_docs:
                    # Check if it's an uploaded document
                    if doc.get('source', '').startswith('uploaded_document_'):
                        # Check access permissions
                        if user_role is None or self.vector_service._can_access_document(doc, user_role):
                            metadata = doc.get('metadata', {})
                            filename = metadata.get('filename', 'Unknown')
                            
                            # Only add each document once (use filename as key)
                            if filename not in documents:
                                documents[filename] = {
                                    'filename': filename,
                                    'file_type': metadata.get('file_type', 'Unknown'),
                                    'chunks': metadata.get('total_chunks', 1),
                                    'source': doc.get('source', ''),
                                    'uploaded_at': metadata.get('uploaded_at', 'Unknown')
                                }
            
            return list(documents.values())
            
        except Exception as e:
            logger.error(f"Get uploaded documents error: {e}")
            return []
    
    def delete_document(self, filename: str, user_role: str = None) -> Dict[str, Any]:
        """Delete a document and its chunks from the vector database."""
        try:
            if not self.vector_service:
                return {'success': False, 'error': 'Vector service not available'}
            
            # Find and remove all chunks for this document
            removed_chunks = 0
            documents_to_remove = []
            embeddings_to_remove = []
            
            target_source = f'uploaded_document_{filename}'
            logger.info(f"Attempting to delete document with source: {target_source}")
            
            for i, doc in enumerate(self.vector_service.documents):
                doc_source = doc.get('source', '')
                # Use exact match for the source to avoid partial matches
                if doc_source == target_source:
                    # Check access permissions
                    if user_role is None or self.vector_service._can_access_document(doc, user_role):
                        documents_to_remove.append(i)
                        embeddings_to_remove.append(i)
                        removed_chunks += 1
            
            logger.info(f"Total chunks to remove for {filename}: {removed_chunks}")
            
            # Remove documents and embeddings in reverse order to maintain indices
            for i in reversed(documents_to_remove):
                if i < len(self.vector_service.documents):
                    del self.vector_service.documents[i]
            
            for i in reversed(embeddings_to_remove):
                if i < len(self.vector_service.embeddings):
                    del self.vector_service.embeddings[i]
            
            # Save changes
            self.vector_service._save_documents()
            
            return {
                'success': True,
                'filename': filename,
                'chunks_removed': removed_chunks
            }
            
        except Exception as e:
            logger.error(f"Delete document error: {e}")
            return {
                'success': False,
                'error': f'Failed to delete document: {str(e)}'
            }
