import os
import logging
import requests
from typing import List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class OutlookService:
    def __init__(self):
        self.client_id = os.getenv('MICROSOFT_CLIENT_ID')
        self.client_secret = os.getenv('MICROSOFT_CLIENT_SECRET')
        self.tenant_id = os.getenv('MICROSOFT_TENANT_ID')
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.access_token = None
        self.last_sync_time = None
        
        # Check if credentials are properly configured
        if not self.client_id or self.client_id == 'your_microsoft_client_id':
            logger.warning("Microsoft client ID not configured. Set MICROSOFT_CLIENT_ID in your .env file")
        if not self.client_secret or self.client_secret == 'your_microsoft_client_secret':
            logger.warning("Microsoft client secret not configured. Set MICROSOFT_CLIENT_SECRET in your .env file")
        if not self.tenant_id or self.tenant_id == 'your_microsoft_tenant_id':
            logger.warning("Microsoft tenant ID not configured. Set MICROSOFT_TENANT_ID in your .env file")
        
    def is_connected(self) -> bool:
        """Check if Outlook is properly configured."""
        return bool(self.client_id and self.client_secret and self.tenant_id and
                   self.client_id != 'your_microsoft_client_id' and
                   self.client_secret != 'your_microsoft_client_secret' and
                   self.tenant_id != 'your_microsoft_tenant_id')
    
    def get_last_sync_time(self) -> str:
        """Get the last sync time as a string."""
        if self.last_sync_time:
            return self.last_sync_time.isoformat()
        return None
    
    def sync_data(self) -> Dict[str, Any]:
        """Sync data from Outlook."""
        try:
            if not self.is_connected():
                return {'count': 0, 'error': 'Outlook not configured. Please set MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET, and MICROSOFT_TENANT_ID in your .env file'}
            
            # Get access token
            if not self._get_access_token():
                return {'count': 0, 'error': 'Failed to get access token. Please check your Microsoft credentials'}
            
            # Get emails
            emails = self._get_emails()
            
            # Update last sync time
            self.last_sync_time = datetime.now()
            
            return {
                'count': len(emails),
                'emails': emails
            }
            
        except Exception as e:
            logger.error(f"Outlook sync error: {e}")
            return {'count': 0, 'error': str(e)}
    
    def _get_access_token(self) -> bool:
        """Get access token from Microsoft Graph."""
        try:
            token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
            
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'https://graph.microsoft.com/.default',
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            
            return bool(self.access_token)
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                logger.error("Microsoft authentication failed. Please check your MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET, and MICROSOFT_TENANT_ID")
            elif e.response.status_code == 401:
                logger.error("Microsoft authentication failed. Please check your credentials and ensure the app is registered in Azure AD")
            else:
                logger.error(f"Get access token error: {e}")
            return False
        except Exception as e:
            logger.error(f"Get access token error: {e}")
            return False
    
    def _get_emails(self, folder: str = 'inbox', limit: int = 100) -> List[Dict]:
        """Get emails from a specific folder."""
        try:
            if not self.access_token:
                return []
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Get emails from the specified folder
            url = f"{self.base_url}/me/mailFolders/{folder}/messages"
            params = {
                '$top': limit,
                '$orderby': 'receivedDateTime desc',
                '$select': 'id,subject,bodyPreview,receivedDateTime,from,toRecipients,isRead'
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            emails = []
            for email in response.json().get('value', []):
                email_data = {
                    'id': email['id'],
                    'subject': email.get('subject', ''),
                    'body_preview': email.get('bodyPreview', ''),
                    'received_date': email.get('receivedDateTime'),
                    'from': email.get('from', {}).get('emailAddress', {}).get('address', ''),
                    'to': [recipient.get('emailAddress', {}).get('address', '') 
                           for recipient in email.get('toRecipients', [])],
                    'is_read': email.get('isRead', False),
                    'source': 'outlook'
                }
                
                # Add metadata
                metadata = {
                    'folder': folder,
                    'from_email': email.get('from', {}).get('emailAddress', {}).get('address', ''),
                    'received_date': email.get('receivedDateTime'),
                    'is_read': email.get('isRead', False),
                    'tags': ['outlook', 'email', f'outlook-{folder}']
                }
                
                email_data['metadata'] = metadata
                emails.append(email_data)
            
            return emails
            
        except Exception as e:
            logger.error(f"Get emails error: {e}")
            return []
    
    def _get_unread_emails(self, limit: int = 50) -> List[Dict]:
        """Get unread emails."""
        try:
            if not self.access_token:
                return []
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}/me/messages"
            params = {
                '$filter': 'isRead eq false',
                '$top': limit,
                '$orderby': 'receivedDateTime desc',
                '$select': 'id,subject,bodyPreview,receivedDateTime,from,toRecipients'
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            emails = []
            for email in response.json().get('value', []):
                email_data = {
                    'id': email['id'],
                    'subject': email.get('subject', ''),
                    'body_preview': email.get('bodyPreview', ''),
                    'received_date': email.get('receivedDateTime'),
                    'from': email.get('from', {}).get('emailAddress', {}).get('address', ''),
                    'to': [recipient.get('emailAddress', {}).get('address', '') 
                           for recipient in email.get('toRecipients', [])],
                    'source': 'outlook'
                }
                
                # Add metadata
                metadata = {
                    'from_email': email.get('from', {}).get('emailAddress', {}).get('address', ''),
                    'received_date': email.get('receivedDateTime'),
                    'is_read': False,
                    'tags': ['outlook', 'email', 'unread']
                }
                
                email_data['metadata'] = metadata
                emails.append(email_data)
            
            return emails
            
        except Exception as e:
            logger.error(f"Get unread emails error: {e}")
            return []
    
    def _get_email_folders(self) -> List[Dict]:
        """Get list of email folders."""
        try:
            if not self.access_token:
                return []
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}/me/mailFolders"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            folders = []
            for folder in response.json().get('value', []):
                folders.append({
                    'id': folder['id'],
                    'name': folder['displayName'],
                    'total_item_count': folder.get('totalItemCount', 0),
                    'unread_item_count': folder.get('unreadItemCount', 0)
                })
            
            return folders
            
        except Exception as e:
            logger.error(f"Get email folders error: {e}")
            return []
    
    def mark_email_as_read(self, email_id: str) -> bool:
        """Mark an email as read."""
        try:
            if not self.access_token:
                return False
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}/me/messages/{email_id}"
            data = {
                'isRead': True
            }
            
            response = requests.patch(url, headers=headers, json=data)
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            logger.error(f"Mark email as read error: {e}")
            return False
