from flask import Blueprint, request, jsonify, session
import logging
import os
from werkzeug.utils import secure_filename
from services.document_service import DocumentService
from datetime import datetime

logger = logging.getLogger(__name__)
bp = Blueprint('documents', __name__, url_prefix='/documents')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload', methods=['POST'])
def upload_document():
    """Upload and process one or more documents."""
    try:
        if 'user_email' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_role = session.get('user_role', 'user')
        
        # Check if files were uploaded
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        
        # Check if files were selected
        if not files or all(file.filename == '' for file in files):
            return jsonify({'error': 'No files selected'}), 400
        
        # Create document service
        doc_service = DocumentService()
        
        results = []
        total_chunks_added = 0
        total_files_processed = 0
        duplicates_found = []
        
        for file in files:
            if file.filename == '':
                continue
                
            # Check file extension
            if not allowed_file(file.filename):
                results.append({
                    'filename': file.filename,
                    'success': False,
                    'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
                })
                continue
            
            # Secure the filename
            filename = secure_filename(file.filename)
            
            # Check for duplicate before processing
            if doc_service.check_duplicate_file(filename, user_role):
                duplicates_found.append(filename)
                results.append({
                    'filename': filename,
                    'success': False,
                    'error': 'File already exists',
                    'duplicate': True
                })
                continue
            
            # Save file temporarily
            temp_path = os.path.join(doc_service.upload_dir, filename)
            file.save(temp_path)
            
            try:
                # Process the document
                result = doc_service.process_document(temp_path, filename, user_role)
                
                if result['success']:
                    total_chunks_added += result['chunks_added']
                    total_files_processed += 1
                    results.append({
                        'filename': filename,
                        'success': True,
                        'chunks_added': result['chunks_added'],
                        'total_chunks': result['total_chunks'],
                        'file_size': result['file_size']
                    })
                else:
                    results.append({
                        'filename': filename,
                        'success': False,
                        'error': result['error']
                    })
                    
            except Exception as e:
                logger.error(f"Error processing file {filename}: {e}")
                results.append({
                    'filename': filename,
                    'success': False,
                    'error': f'Failed to process document: {str(e)}'
                })
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        # Return summary and individual results
        return jsonify({
            'message': f'Processed {len(files)} files',
            'total_files_processed': total_files_processed,
            'total_chunks_added': total_chunks_added,
            'duplicates_found': duplicates_found,
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Document upload error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/list', methods=['GET'])
def list_documents():
    """Get list of uploaded documents."""
    try:
        if 'user_email' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_role = session.get('user_role', 'user')
        
        doc_service = DocumentService()
        documents = doc_service.get_uploaded_documents(user_role)
        
        return jsonify({
            'documents': documents,
            'count': len(documents)
        }), 200
        
    except Exception as e:
        logger.error(f"List documents error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/delete/<filename>', methods=['DELETE'])
def delete_document(filename):
    """Delete an uploaded document."""
    try:
        if 'user_email' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_role = session.get('user_role', 'user')
        
        # Log the original filename before securing
        original_filename = filename
        logger.info(f"Delete request received for original filename: {original_filename}")
        
        # Secure the filename
        filename = secure_filename(filename)
        logger.info(f"Secured filename: {filename}")
        
        logger.info(f"Delete request received for filename: {filename}")
        logger.info(f"User: {session.get('user_email')}, Role: {user_role}")
        
        doc_service = DocumentService()
        result = doc_service.delete_document(filename, user_role)
        
        logger.info(f"Delete result for {filename}: {result}")
        
        if result['success']:
            return jsonify({
                'message': 'Document deleted successfully',
                'filename': filename,
                'chunks_removed': result['chunks_removed']
            }), 200
        else:
            return jsonify({'error': result['error']}), 400
        
    except Exception as e:
        logger.error(f"Delete document error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/search', methods=['POST'])
def search_documents():
    """Search within uploaded documents."""
    try:
        if 'user_email' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.get_json()
        query = data.get('query')
        user_role = session.get('user_role', 'user')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Use the existing vector service for search
        from services.vector_service import VectorService
        vector_service = VectorService()
        
        # Search for documents with uploaded_document source
        results = vector_service.search(query, user_role)
        
        # Filter to only uploaded documents
        uploaded_results = [
            result for result in results 
            if result.get('source', '').startswith('uploaded_document_')
        ]
        
        return jsonify({
            'query': query,
            'results': uploaded_results,
            'count': len(uploaded_results)
        }), 200
        
    except Exception as e:
        logger.error(f"Search documents error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/save', methods=['POST'])
def save_documents():
    """Manually trigger saving documents to disk."""
    try:
        if 'user_email' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        # Get the document service which has access to the vector service
        doc_service = DocumentService()
        
        # Force save using the document service's vector service
        doc_service.vector_service._save_documents()
        
        # Check if save was successful
        import os
        docs_file = os.path.join(doc_service.vector_service.vector_db_path, 'documents.json')
        embeddings_file = os.path.join(doc_service.vector_service.vector_db_path, 'embeddings.json')
        
        docs_saved = os.path.exists(docs_file) and os.path.getsize(docs_file) > 2
        embeddings_saved = os.path.exists(embeddings_file) and os.path.getsize(embeddings_file) > 2
        
        return jsonify({
            'message': 'Documents saved to disk',
            'documents_saved': docs_saved,
            'embeddings_saved': embeddings_saved,
            'documents_count': len(doc_service.vector_service.documents),
            'embeddings_count': len(doc_service.vector_service.embeddings)
        }), 200
        
    except Exception as e:
        logger.error(f"Save documents error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/replace', methods=['POST'])
def replace_document():
    """Replace an existing document with a new one."""
    try:
        if 'user_email' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_role = session.get('user_role', 'user')
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({
                'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Create document service
        doc_service = DocumentService()
        
        # Save file temporarily
        temp_path = os.path.join(doc_service.upload_dir, filename)
        file.save(temp_path)
        
        try:
            # Process the document with replace flag
            result = doc_service.process_document(temp_path, filename, user_role, replace_existing=True)
            
            if result['success']:
                return jsonify({
                    'message': 'Document replaced successfully',
                    'filename': filename,
                    'chunks_added': result['chunks_added'],
                    'total_chunks': result['total_chunks'],
                    'file_size': result['file_size'],
                    'replaced': True
                }), 200
            else:
                return jsonify({'error': result['error']}), 400
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
    except Exception as e:
        logger.error(f"Document replace error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
