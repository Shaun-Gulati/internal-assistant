from flask import Blueprint, request, jsonify, session
import logging
from services.slack_service import SlackService
from services.github_service import GitHubService
from services.outlook_service import OutlookService

logger = logging.getLogger(__name__)
bp = Blueprint('integrations', __name__, url_prefix='/integrations')

@bp.route('/', methods=['GET'])
def get_integrations():
    """Get status of all integrations (alias for /status)."""
    return get_integration_status()

@bp.route('/status', methods=['GET'])
def get_integration_status():
    """Get status of all integrations."""
    try:
        if 'user_email' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        slack_service = SlackService()
        github_service = GitHubService()
        outlook_service = OutlookService()
        
        return jsonify({
            'slack': {
                'connected': slack_service.is_connected(),
                'last_sync': slack_service.get_last_sync_time()
            },
            'github': {
                'connected': github_service.is_connected(),
                'last_sync': github_service.get_last_sync_time()
            },
            'outlook': {
                'connected': outlook_service.is_connected(),
                'last_sync': outlook_service.get_last_sync_time()
            }
        })
        
    except Exception as e:
        logger.error(f"Integration status error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/slack/sync', methods=['POST'])
def sync_slack():
    """Sync Slack data."""
    try:
        if 'user_email' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        slack_service = SlackService()
        result = slack_service.sync_data()
        
        return jsonify({
            'success': True,
            'message': f"Synced {result['count']} messages from Slack",
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Slack sync error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/github/sync', methods=['POST'])
def sync_github():
    """Sync GitHub data."""
    try:
        if 'user_email' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        github_service = GitHubService()
        result = github_service.sync_data()
        
        return jsonify({
            'success': True,
            'message': f"Synced {result['count']} items from GitHub",
            'data': result
        })
        
    except Exception as e:
        logger.error(f"GitHub sync error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/outlook/sync', methods=['POST'])
def sync_outlook():
    """Sync Outlook data."""
    try:
        if 'user_email' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        outlook_service = OutlookService()
        result = outlook_service.sync_data()
        
        return jsonify({
            'success': True,
            'message': f"Synced {result['count']} emails from Outlook",
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Outlook sync error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/sync/all', methods=['POST'])
def sync_all():
    """Sync all integrations."""
    try:
        if 'user_email' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        slack_service = SlackService()
        github_service = GitHubService()
        outlook_service = OutlookService()
        
        results = {
            'slack': slack_service.sync_data(),
            'github': github_service.sync_data(),
            'outlook': outlook_service.sync_data()
        }
        
        total_count = sum(result['count'] for result in results.values())
        
        return jsonify({
            'success': True,
            'message': f"Synced {total_count} total items",
            'data': results
        })
        
    except Exception as e:
        logger.error(f"Sync all error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
