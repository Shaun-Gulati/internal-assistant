#!/usr/bin/env python3
"""
Graceful shutdown helper for Flask application.
This script helps prevent semaphore leaks and ensures clean shutdown.
"""

import os
import sys
import signal
import multiprocessing
import logging
from multiprocessing import resource_tracker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_multiprocessing():
    """Clean up multiprocessing resources to prevent semaphore leaks."""
    try:
        # Clean up any remaining multiprocessing resources
        if hasattr(multiprocessing, 'resource_tracker'):
            # Force cleanup of resource tracker (handle different Python versions)
            try:
                if hasattr(resource_tracker, '_CLEANUP_CALLBACKS'):
                    resource_tracker._CLEANUP_CALLBACKS.clear()
                elif hasattr(resource_tracker, '_REGISTRY'):
                    resource_tracker._REGISTRY.clear()
            except (AttributeError, TypeError):
                # Resource tracker cleanup not available in this Python version
                pass
        
        # Clean up any remaining processes
        for process in multiprocessing.active_children():
            if process.is_alive():
                logger.info(f"Terminating child process: {process.name}")
                process.terminate()
                process.join(timeout=5)
                if process.is_alive():
                    logger.warning(f"Force killing child process: {process.name}")
                    process.kill()
                    process.join()
        
        logger.info("Multiprocessing cleanup completed")
    except Exception as e:
        logger.error(f"Error during multiprocessing cleanup: {e}")

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    logger.info("Received shutdown signal, cleaning up...")
    cleanup_multiprocessing()
    sys.exit(0)

def setup_graceful_shutdown():
    """Setup graceful shutdown handlers."""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Set multiprocessing start method to prevent semaphore leaks
    try:
        multiprocessing.set_start_method('spawn', force=True)
        logger.info("Multiprocessing start method set to 'spawn'")
    except RuntimeError:
        logger.info("Multiprocessing start method already set")
    
    # Register cleanup function to run at exit
    import atexit
    atexit.register(cleanup_multiprocessing)

if __name__ == '__main__':
    setup_graceful_shutdown()
    logger.info("Graceful shutdown setup completed")
