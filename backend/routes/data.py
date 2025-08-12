from flask import Blueprint, request, jsonify, session
import logging
from services.data_service import DataService

logger = logging.getLogger(__name__)
bp = Blueprint('data', __name__, url_prefix='/data')

@bp.route('/summary', methods=['GET'])
def get_data_summary():
    """Get summary of aggregated data."""
    try:
        if 'user_email' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_role = session.get('user_role', 'user')
        data_service = DataService()
        
        summary = data_service.get_summary(user_role)
        
        return jsonify(summary)
        
    except Exception as e:
        logger.error(f"Data summary error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/slack', methods=['GET'])
def get_slack_data():
    """Get Slack data for the current user."""
    try:
        if 'user_email' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_role = session.get('user_role', 'user')
        data_service = DataService()
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        channel = request.args.get('channel')
        
        slack_data = data_service.get_slack_data(user_role, limit=limit, channel=channel)
        
        return jsonify(slack_data)
        
    except Exception as e:
        logger.error(f"Slack data error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/github', methods=['GET'])
def get_github_data():
    """Get GitHub data for the current user."""
    try:
        if 'user_email' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_role = session.get('user_role', 'user')
        data_service = DataService()
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        repo = request.args.get('repo')
        data_type = request.args.get('type', 'all')  # commits, prs, issues
        
        github_data = data_service.get_github_data(user_role, limit=limit, repo=repo, data_type=data_type)
        
        return jsonify(github_data)
        
    except Exception as e:
        logger.error(f"GitHub data error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/outlook', methods=['GET'])
def get_outlook_data():
    """Get Outlook data for the current user."""
    try:
        if 'user_email' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_role = session.get('user_role', 'user')
        data_service = DataService()
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        folder = request.args.get('folder', 'inbox')
        
        outlook_data = data_service.get_outlook_data(user_role, limit=limit, folder=folder)
        
        return jsonify(outlook_data)
        
    except Exception as e:
        logger.error(f"Outlook data error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/search', methods=['GET'])
def search_data():
    """Search across all data sources."""
    try:
        if 'user_email' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_role = session.get('user_role', 'user')
        query = request.args.get('q')
        source = request.args.get('source', 'all')  # slack, github, outlook, all
        limit = request.args.get('limit', 20, type=int)
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        data_service = DataService()
        search_results = data_service.search_data(query, user_role, source=source, limit=limit)
        
        return jsonify(search_results)
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
