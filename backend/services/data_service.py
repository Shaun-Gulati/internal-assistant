import os
import logging
from typing import List, Dict, Any
from services.slack_service import SlackService
from services.github_service import GitHubService
from services.outlook_service import OutlookService
from services.vector_service import VectorService

logger = logging.getLogger(__name__)

class DataService:
    def __init__(self):
        # Initialize services with error handling
        try:
            self.slack_service = SlackService()
        except Exception as e:
            logger.warning(f"Failed to initialize SlackService: {e}")
            self.slack_service = None
            
        try:
            self.github_service = GitHubService()
        except Exception as e:
            logger.warning(f"Failed to initialize GitHubService: {e}")
            self.github_service = None
            
        try:
            self.outlook_service = OutlookService()
        except Exception as e:
            logger.warning(f"Failed to initialize OutlookService: {e}")
            self.outlook_service = None
            
        try:
            self.vector_service = VectorService()
        except Exception as e:
            logger.warning(f"Failed to initialize VectorService: {e}")
            self.vector_service = None
        
    def get_summary(self, user_role: str) -> Dict[str, Any]:
        """Get a summary of all data for the user."""
        try:
            summary = {
                'slack': self._get_slack_summary(user_role),
                'github': self._get_github_summary(user_role),
                'outlook': self._get_outlook_summary(user_role),
                'total_items': 0
            }
            
            # Calculate total items
            summary['total_items'] = (
                summary['slack']['count'] +
                summary['github']['count'] +
                summary['outlook']['count']
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Get summary error: {e}")
            return {
                'slack': {'count': 0, 'channels': 0, 'mentions': 0},
                'github': {'count': 0, 'repos': 0, 'commits': 0, 'prs': 0, 'issues': 0},
                'outlook': {'count': 0, 'unread': 0, 'folders': 0},
                'total_items': 0
            }
    
    def get_slack_data(self, user_role: str, limit: int = 50, channel: str = None) -> Dict[str, Any]:
        """Get Slack data filtered by user role."""
        try:
            if not self._can_access_source('slack', user_role):
                return {'data': [], 'count': 0, 'error': 'Access denied'}
            
            # Try to get real Slack data if service is available and connected
            if self.slack_service and self.slack_service.is_connected():
                # Get channels first
                channels = self.slack_service._get_channels()
                
                # If channel filter is specified, find the channel ID
                target_channel_id = None
                if channel:
                    for ch in channels:
                        if ch['name'] == channel:
                            target_channel_id = ch['id']
                            break
                
                # Get messages from all channels or specific channel
                all_messages = []
                if target_channel_id:
                    messages = self.slack_service._get_channel_messages(target_channel_id, limit)
                    all_messages.extend(messages)
                else:
                    # Get messages from all accessible channels
                    for ch in channels[:5]:  # Limit to first 5 channels for performance
                        messages = self.slack_service._get_channel_messages(ch['id'], limit // len(channels))
                        all_messages.extend(messages)
                
                # Transform Slack messages to match expected format
                transformed_messages = []
                for msg in all_messages[:limit]:
                    transformed_msg = {
                        'id': msg['id'],
                        'text': msg['text'],
                        'user': msg['user'],
                        'channel': self._get_channel_name_by_id(channels, msg['channel_id']),
                        'timestamp': msg['timestamp'],
                        'source': 'slack'
                    }
                    transformed_messages.append(transformed_msg)
                
                return {
                    'data': transformed_messages,
                    'count': len(transformed_messages),
                    'source': 'slack',
                    'real_data': True
                }
            else:
                # Return empty data when Slack is not connected
                return {
                    'data': [],
                    'count': 0,
                    'source': 'slack',
                    'real_data': False,
                    'error': 'Slack not connected'
                }
            
        except Exception as e:
            logger.error(f"Get Slack data error: {e}")
            return {'data': [], 'count': 0, 'error': str(e)}
    
    def get_github_data(self, user_role: str, limit: int = 50, repo: str = None, data_type: str = 'all') -> Dict[str, Any]:
        """Get GitHub data filtered by user role."""
        try:
            if not self._can_access_source('github', user_role):
                return {'data': [], 'count': 0, 'error': 'Access denied'}
            
            # For MVP, we'll return mock data
            # In production, this would query the actual GitHub data
            mock_data = self._get_mock_github_data(limit, repo, data_type)
            
            return {
                'data': mock_data,
                'count': len(mock_data),
                'source': 'github'
            }
            
        except Exception as e:
            logger.error(f"Get GitHub data error: {e}")
            return {'data': [], 'count': 0, 'error': str(e)}
    
    def get_outlook_data(self, user_role: str, limit: int = 50, folder: str = 'inbox') -> Dict[str, Any]:
        """Get Outlook data filtered by user role."""
        try:
            if not self._can_access_source('outlook', user_role):
                return {'data': [], 'count': 0, 'error': 'Access denied'}
            
            # For MVP, we'll return mock data
            # In production, this would query the actual Outlook data
            mock_data = self._get_mock_outlook_data(limit, folder)
            
            return {
                'data': mock_data,
                'count': len(mock_data),
                'source': 'outlook'
            }
            
        except Exception as e:
            logger.error(f"Get Outlook data error: {e}")
            return {'data': [], 'count': 0, 'error': str(e)}
    
    def search_data(self, query: str, user_role: str, source: str = 'all', limit: int = 20) -> Dict[str, Any]:
        """Search across all data sources."""
        try:
            # Use vector service for semantic search if available
            if self.vector_service:
                results = self.vector_service.search(query, user_role, limit=limit)
            else:
                # Fallback to simple text search
                results = self._simple_search(query, user_role, limit=limit)
            
            return {
                'query': query,
                'results': results,
                'count': len(results),
                'source': source
            }
            
        except Exception as e:
            logger.error(f"Search data error: {e}")
            return {'results': [], 'count': 0, 'error': str(e)}
    
    def _get_slack_summary(self, user_role: str) -> Dict[str, Any]:
        """Get Slack summary for user role."""
        if not self._can_access_source('slack', user_role):
            return {'count': 0, 'channels': 0, 'mentions': 0}
        
        # Try to get real Slack data if service is available and connected
        if self.slack_service and self.slack_service.is_connected():
            try:
                # Get channels
                channels = self.slack_service._get_channels()
                
                # Get total message count from all channels
                total_messages = 0
                for channel in channels[:5]:  # Limit to first 5 channels for performance
                    messages = self.slack_service._get_channel_messages(channel['id'], 100)
                    total_messages += len(messages)
                
                return {
                    'count': total_messages,
                    'channels': len(channels),
                    'mentions': 0,  # TODO: Implement mentions counting
                    'last_sync': self.slack_service.get_last_sync_time(),
                    'real_data': True
                }
            except Exception as e:
                logger.error(f"Error getting real Slack summary: {e}")
                # Return zero counts on error
                return {
                    'count': 0,
                    'channels': 0,
                    'mentions': 0,
                    'last_sync': None,
                    'real_data': False,
                    'error': str(e)
                }
        else:
            # Return zero counts when Slack is not connected
            return {
                'count': 0,
                'channels': 0,
                'mentions': 0,
                'last_sync': None,
                'real_data': False,
                'error': 'Slack not connected'
            }
    
    def _get_github_summary(self, user_role: str) -> Dict[str, Any]:
        """Get GitHub summary for user role."""
        if not self._can_access_source('github', user_role):
            return {'count': 0, 'repos': 0, 'commits': 0, 'prs': 0, 'issues': 0}
        
        return {
            'count': 85,  # Mock count
            'repos': 8,
            'commits': 45,
            'prs': 25,
            'issues': 15,
            'last_sync': '2024-01-15T10:30:00Z'
        }
    
    def _get_outlook_summary(self, user_role: str) -> Dict[str, Any]:
        """Get Outlook summary for user role."""
        if not self._can_access_source('outlook', user_role):
            return {'count': 0, 'unread': 0, 'folders': 0}
        
        return {
            'count': 200,  # Mock count
            'unread': 25,
            'folders': 3,
            'last_sync': '2024-01-15T10:30:00Z'
        }
    
    def _can_access_source(self, source: str, user_role: str) -> bool:
        """Check if user can access a specific data source."""
        # Admin can access everything
        if user_role == 'admin':
            return True
        
        # Role-based access rules
        role_access_rules = {
            'developer': ['slack', 'github'],
            'marketing': ['slack', 'outlook'],
            'sales': ['slack', 'outlook'],
            'user': ['slack']  # Default access
        }
        
        allowed_sources = role_access_rules.get(user_role, ['slack'])
        return source in allowed_sources
    
    def _simple_search(self, query: str, user_role: str, limit: int = 20) -> List[Dict]:
        """Simple text search fallback when vector service is not available."""
        # Combine all mock data and search
        all_data = []
        
        # Only include Slack data if connected
        if self.slack_service and self.slack_service.is_connected():
            all_data.extend(self._get_mock_slack_data(50))
        
        all_data.extend(self._get_mock_github_data(50))
        all_data.extend(self._get_mock_outlook_data(50))
        
        # Simple text search
        query_lower = query.lower()
        results = []
        
        for item in all_data:
            # Search in text content
            if 'text' in item and query_lower in item['text'].lower():
                results.append(item)
            elif 'message' in item and query_lower in item['message'].lower():
                results.append(item)
            elif 'subject' in item and query_lower in item['subject'].lower():
                results.append(item)
            elif 'title' in item and query_lower in item['title'].lower():
                results.append(item)
        
        return results[:limit]
    
    def _get_channel_name_by_id(self, channels: List[Dict], channel_id: str) -> str:
        """Get channel name by channel ID."""
        for channel in channels:
            if channel['id'] == channel_id:
                return channel['name']
        return 'unknown'
    
    def _get_mock_slack_data(self, limit: int, channel: str = None) -> List[Dict]:
        """Get mock Slack data for MVP."""
        mock_messages = [
            {
                'id': 'msg1',
                'text': 'Hey team, we have a new feature release tomorrow!',
                'user': 'john.doe',
                'channel': 'general',
                'timestamp': '2024-01-15T10:30:00Z',
                'source': 'slack'
            },
            {
                'id': 'msg2',
                'text': 'Can someone review the latest PR?',
                'user': 'jane.smith',
                'channel': 'dev-team',
                'timestamp': '2024-01-15T09:15:00Z',
                'source': 'slack'
            },
            {
                'id': 'msg3',
                'text': 'Great work on the marketing campaign!',
                'user': 'marketing.lead',
                'channel': 'marketing',
                'timestamp': '2024-01-15T08:45:00Z',
                'source': 'slack'
            }
        ]
        
        if channel:
            mock_messages = [msg for msg in mock_messages if msg['channel'] == channel]
        
        return mock_messages[:limit]
    
    def _get_mock_github_data(self, limit: int, repo: str = None, data_type: str = 'all') -> List[Dict]:
        """Get mock GitHub data for MVP."""
        mock_data = [
            {
                'id': 'commit1',
                'message': 'Add new authentication feature',
                'author': 'john.doe',
                'repo': 'internal-app',
                'type': 'commit',
                'timestamp': '2024-01-15T10:30:00Z',
                'source': 'github'
            },
            {
                'id': 'pr1',
                'title': 'Implement user dashboard',
                'author': 'jane.smith',
                'repo': 'internal-app',
                'type': 'pull_request',
                'state': 'open',
                'timestamp': '2024-01-15T09:15:00Z',
                'source': 'github'
            },
            {
                'id': 'issue1',
                'title': 'Bug: Login page not loading',
                'author': 'user.report',
                'repo': 'internal-app',
                'type': 'issue',
                'state': 'open',
                'timestamp': '2024-01-15T08:45:00Z',
                'source': 'github'
            }
        ]
        
        if repo:
            mock_data = [item for item in mock_data if item['repo'] == repo]
        
        if data_type != 'all':
            mock_data = [item for item in mock_data if item['type'] == data_type]
        
        return mock_data[:limit]
    
    def _get_mock_outlook_data(self, limit: int, folder: str = 'inbox') -> List[Dict]:
        """Get mock Outlook data for MVP."""
        mock_emails = [
            {
                'id': 'email1',
                'subject': 'Weekly Team Update',
                'from': 'manager@company.com',
                'body_preview': 'Here is this week\'s team update...',
                'folder': 'inbox',
                'is_read': False,
                'timestamp': '2024-01-15T10:30:00Z',
                'source': 'outlook'
            },
            {
                'id': 'email2',
                'subject': 'Project Status Report',
                'from': 'project.lead@company.com',
                'body_preview': 'The project is progressing well...',
                'folder': 'inbox',
                'is_read': True,
                'timestamp': '2024-01-15T09:15:00Z',
                'source': 'outlook'
            },
            {
                'id': 'email3',
                'subject': 'Client Meeting Tomorrow',
                'from': 'client@external.com',
                'body_preview': 'Looking forward to our meeting...',
                'folder': 'inbox',
                'is_read': False,
                'timestamp': '2024-01-15T08:45:00Z',
                'source': 'outlook'
            }
        ]
        
        if folder != 'inbox':
            mock_emails = [email for email in mock_emails if email['folder'] == folder]
        
        return mock_emails[:limit]
