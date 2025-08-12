import os
import logging
import requests
from typing import List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SlackService:
    def __init__(self):
        self.bot_token = os.getenv('SLACK_BOT_TOKEN')
        self.app_token = os.getenv('SLACK_APP_TOKEN')
        self.signing_secret = os.getenv('SLACK_SIGNING_SECRET')
        self.base_url = "https://slack.com/api"
        self.last_sync_time = None
        
    def is_connected(self) -> bool:
        """Check if Slack is properly configured."""
        # Check if tokens exist and are not placeholder values
        if not (self.bot_token and self.app_token):
            return False
        
        # Check if tokens are not placeholder values
        if (self.bot_token == 'xoxb-your-slack-bot-token' or 
            self.app_token == 'xapp-your-slack-app-token' or
            self.signing_secret == 'your-slack-signing-secret'):
            return False
        
        # Optionally test the API connection (but this might be slow)
        # Uncomment the following lines if you want to validate tokens on every check
        # try:
        #     headers = {'Authorization': f'Bearer {self.bot_token}'}
        #     response = requests.get(f"{self.base_url}/auth.test", headers=headers)
        #     return response.json().get('ok', False)
        # except:
        #     return False
        
        return True
    
    def get_last_sync_time(self) -> str:
        """Get the last sync time as a string."""
        if self.last_sync_time:
            return self.last_sync_time.isoformat()
        return None
    
    def sync_data(self) -> Dict[str, Any]:
        """Sync data from Slack."""
        try:
            if not self.is_connected():
                return {'count': 0, 'error': 'Slack not configured'}
            
            # Get channels
            channels = self._get_channels()
            
            # Get messages from each channel
            all_messages = []
            for channel in channels:
                messages = self._get_channel_messages(channel['id'])
                all_messages.extend(messages)
            
            # Update last sync time
            self.last_sync_time = datetime.now()
            
            return {
                'count': len(all_messages),
                'channels': len(channels),
                'messages': all_messages
            }
            
        except Exception as e:
            logger.error(f"Slack sync error: {e}")
            return {'count': 0, 'error': str(e)}
    
    def _get_channels(self) -> List[Dict]:
        """Get list of channels."""
        try:
            headers = {
                'Authorization': f'Bearer {self.bot_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f"{self.base_url}/conversations.list", headers=headers)
            response.raise_for_status()
            
            data = response.json()
            if not data.get('ok'):
                logger.error(f"Slack API error: {data.get('error')}")
                return []
            
            # Filter for public channels only
            channels = [
                {
                    'id': channel['id'],
                    'name': channel['name'],
                    'is_private': channel.get('is_private', False)
                }
                for channel in data.get('channels', [])
                if not channel.get('is_private', False)  # Only public channels for MVP
            ]
            
            return channels
            
        except Exception as e:
            logger.error(f"Get channels error: {e}")
            return []
    
    def _get_channel_messages(self, channel_id: str, limit: int = 100) -> List[Dict]:
        """Get messages from a specific channel."""
        try:
            headers = {
                'Authorization': f'Bearer {self.bot_token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'channel': channel_id,
                'limit': limit
            }
            
            response = requests.get(f"{self.base_url}/conversations.history", headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if not data.get('ok'):
                logger.error(f"Slack API error: {data.get('error')}")
                return []
            
            messages = []
            for msg in data.get('messages', []):
                # Skip bot messages and system messages
                if msg.get('bot_id') or msg.get('subtype'):
                    continue
                
                message_data = {
                    'id': msg['ts'],
                    'text': msg.get('text', ''),
                    'user': msg.get('user', ''),
                    'timestamp': msg['ts'],
                    'channel_id': channel_id,
                    'source': 'slack'
                }
                
                # Add metadata
                metadata = {
                    'channel_id': channel_id,
                    'user_id': msg.get('user', ''),
                    'timestamp': msg['ts'],
                    'tags': ['slack', f'slack-{channel_id}']
                }
                
                message_data['metadata'] = metadata
                messages.append(message_data)
            
            return messages
            
        except Exception as e:
            logger.error(f"Get channel messages error: {e}")
            return []
    
    def get_mentions(self, user_id: str = None) -> List[Dict]:
        """Get messages that mention the user."""
        try:
            if not self.is_connected():
                return []
            
            # For MVP, we'll get all messages and filter for mentions
            # In production, you'd use the search API
            channels = self._get_channels()
            mentions = []
            
            for channel in channels:
                messages = self._get_channel_messages(channel['id'])
                for msg in messages:
                    if user_id and f'<@{user_id}>' in msg.get('text', ''):
                        mentions.append(msg)
            
            return mentions
            
        except Exception as e:
            logger.error(f"Get mentions error: {e}")
            return []
    
    def get_user_info(self, user_id: str) -> Dict:
        """Get user information."""
        try:
            if not self.is_connected():
                return {}
            
            headers = {
                'Authorization': f'Bearer {self.bot_token}',
                'Content-Type': 'application/json'
            }
            
            params = {'user': user_id}
            response = requests.get(f"{self.base_url}/users.info", headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if not data.get('ok'):
                return {}
            
            user = data.get('user', {})
            return {
                'id': user.get('id'),
                'name': user.get('name'),
                'real_name': user.get('real_name'),
                'email': user.get('profile', {}).get('email')
            }
            
        except Exception as e:
            logger.error(f"Get user info error: {e}")
            return {}
