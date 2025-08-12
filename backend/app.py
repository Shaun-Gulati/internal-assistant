from flask import Flask, jsonify, session
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging
import signal
import sys
import multiprocessing

# Import graceful shutdown helper
try:
    from graceful_shutdown import setup_graceful_shutdown, cleanup_multiprocessing
except ImportError:
    # Fallback if helper not available
    def setup_graceful_shutdown():
        pass
    def cleanup_multiprocessing():
        pass

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prevent multiprocessing semaphore leaks
if __name__ == '__main__':
    # Set multiprocessing start method to 'spawn' to prevent semaphore leaks
    multiprocessing.set_start_method('spawn', force=True)

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    logger.info("Received shutdown signal, cleaning up...")
    cleanup_multiprocessing()
    sys.exit(0)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Enable CORS for frontend
    CORS(app, origins=['http://localhost:3000'], supports_credentials=True)
    
    # Register blueprints
    from routes import auth, chat, integrations, data, documents
    app.register_blueprint(auth.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(integrations.bp)
    app.register_blueprint(data.bp)
    app.register_blueprint(documents.bp)
    
    @app.route('/')
    def root():
        """Root endpoint with API information."""
        return jsonify({
            'message': 'Internal Assistant API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/health',
                'auth': {
                    'login': '/auth/login',
                    'logout': '/auth/logout',
                    'user': '/auth/user',
                    'check': '/auth/check'
                },
                'chat': {
                    'send': '/chat/send',
                    'history': '/chat/history'
                },
                'integrations': {
                    'list': '/integrations',
                    'connect': '/integrations/connect',
                    'disconnect': '/integrations/disconnect'
                },
                'data': {
                    'summary': '/data/summary',
                    'search': '/data/search'
                },
                'documents': {
                    'upload': '/documents/upload',
                    'list': '/documents/list',
                    'delete': '/documents/delete/<filename>',
                    'search': '/documents/search',
                    'save': '/documents/save'
                }
            }
        })
    
    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({'status': 'healthy', 'message': 'Internal Assistant API is running'})
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    # Setup graceful shutdown
    setup_graceful_shutdown()
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    app = create_app()
    port = int(os.getenv('BACKEND_PORT', 5000))
    
    # Use threaded mode instead of multiprocessing to prevent semaphore leaks
    # Set use_reloader=False in debug mode to prevent duplicate processes
    debug_mode = app.config['DEBUG']
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=debug_mode,
        use_reloader=False,  # Disable reloader to prevent multiprocessing issues
        threaded=True        # Use threading instead of multiprocessing
    )
