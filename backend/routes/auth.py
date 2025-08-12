from flask import Blueprint, request, jsonify, session
import os
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['POST'])
def login():
    """Handle user login."""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        # Simple authentication for MVP
        allowed_users = os.getenv('ALLOWED_USERS', '').split(',')
        
        if email in allowed_users:
            session['user_email'] = email
            session['user_role'] = get_user_role(email)
            return jsonify({
                'success': True,
                'user': {
                    'email': email,
                    'role': session['user_role']
                }
            })
        else:
            return jsonify({'error': 'Unauthorized'}), 401
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/logout', methods=['POST'])
def logout():
    """Handle user logout."""
    session.clear()
    return jsonify({'success': True})

@bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user information."""
    if 'user_email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return jsonify({
        'email': session['user_email'],
        'role': session.get('user_role', 'user')
    })

@bp.route('/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated."""
    return jsonify({
        'authenticated': 'user_email' in session,
        'user': {
            'email': session.get('user_email'),
            'role': session.get('user_role')
        } if 'user_email' in session else None
    })

def get_user_role(email):
    """Get user role based on email (MVP implementation)."""
    # This would be replaced with a proper role mapping system
    role_mappings = {
        'admin@company.com': 'admin',
        'developer@company.com': 'developer',
        'marketing@company.com': 'marketing',
        'sales@company.com': 'sales'
    }
    return role_mappings.get(email, 'user')
