from flask import Blueprint, request, jsonify, session
import logging
import os
from services.llm_service import LLMService
from services.vector_service import VectorService

logger = logging.getLogger(__name__)
bp = Blueprint('chat', __name__, url_prefix='/chat')

@bp.route('/send', methods=['POST'])
def send_message():
    """Send a message to the AI assistant."""
    try:
        if 'user_email' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.get_json()
        message = data.get('message')
        user_role = session.get('user_role', 'user')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get relevant context based on user role
        vector_service = VectorService()
        relevant_docs = vector_service.search(message, user_role)
        
        # Generate response using LLM
        llm_service = LLMService()
        response = llm_service.generate_response(message, relevant_docs, user_role)
        
        return jsonify({
            'response': response,
            'sources': relevant_docs[:3]  # Return top 3 sources
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/history', methods=['GET'])
def get_chat_history():
    """Get chat history for the current user."""
    try:
        if 'user_email' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        # For MVP, return empty history
        # This would be replaced with a proper chat history system
        return jsonify({'history': []})
        
    except Exception as e:
        logger.error(f"Chat history error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/stream', methods=['POST'])
def stream_message():
    """Stream a message response (for future implementation)."""
    try:
        if 'user_email' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.get_json()
        message = data.get('message')
        user_role = session.get('user_role', 'user')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # For MVP, return regular response
        # This would be replaced with streaming implementation
        vector_service = VectorService()
        relevant_docs = vector_service.search(message, user_role)
        
        llm_service = LLMService()
        response = llm_service.generate_response(message, relevant_docs, user_role)
        
        return jsonify({
            'response': response,
            'sources': relevant_docs[:3]
        })
        
    except Exception as e:
        logger.error(f"Stream chat error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
