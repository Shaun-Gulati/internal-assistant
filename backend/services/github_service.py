import os
import logging
import requests
from typing import List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class GitHubService:
    def __init__(self):
        self.access_token = os.getenv('GITHUB_ACCESS_TOKEN')
        self.org_name = os.getenv('GITHUB_ORG_NAME')
        self.base_url = "https://api.github.com"
        self.last_sync_time = None
        
        # Check if credentials are properly configured
        if not self.access_token or self.access_token == 'your_github_personal_access_token':
            logger.warning("GitHub access token not configured. Set GITHUB_ACCESS_TOKEN in your .env file")
        if not self.org_name or self.org_name == 'your_organization_name':
            logger.warning("GitHub organization name not configured. Set GITHUB_ORG_NAME in your .env file")
        
    def is_connected(self) -> bool:
        """Check if GitHub is properly configured."""
        return bool(self.access_token and self.org_name and 
                   self.access_token != 'your_github_personal_access_token' and
                   self.org_name != 'your_organization_name')
    
    def get_last_sync_time(self) -> str:
        """Get the last sync time as a string."""
        if self.last_sync_time:
            return self.last_sync_time.isoformat()
        return None
    
    def sync_data(self) -> Dict[str, Any]:
        """Sync data from GitHub."""
        try:
            if not self.is_connected():
                return {'count': 0, 'error': 'GitHub not configured. Please set GITHUB_ACCESS_TOKEN and GITHUB_ORG_NAME in your .env file'}
            
            # Get repositories
            repos = self._get_repositories()
            
            all_data = {
                'commits': [],
                'pull_requests': [],
                'issues': []
            }
            
            # Get data from each repository
            for repo in repos:
                repo_name = repo['name']
                
                # Get commits
                commits = self._get_recent_commits(repo_name)
                all_data['commits'].extend(commits)
                
                # Get pull requests
                prs = self._get_pull_requests(repo_name)
                all_data['pull_requests'].extend(prs)
                
                # Get issues
                issues = self._get_issues(repo_name)
                all_data['issues'].extend(issues)
            
            # Update last sync time
            self.last_sync_time = datetime.now()
            
            total_count = len(all_data['commits']) + len(all_data['pull_requests']) + len(all_data['issues'])
            
            return {
                'count': total_count,
                'repositories': len(repos),
                'data': all_data
            }
            
        except Exception as e:
            logger.error(f"GitHub sync error: {e}")
            return {'count': 0, 'error': str(e)}
    
    def _get_repositories(self) -> List[Dict]:
        """Get list of repositories in the organization."""
        try:
            headers = {
                'Authorization': f'token {self.access_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            url = f"{self.base_url}/orgs/{self.org_name}/repos"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            repos = []
            for repo in response.json():
                repos.append({
                    'id': repo['id'],
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'description': repo.get('description', ''),
                    'language': repo.get('language'),
                    'updated_at': repo['updated_at']
                })
            
            return repos
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.error("GitHub authentication failed. Please check your GITHUB_ACCESS_TOKEN")
                return []
            elif e.response.status_code == 404:
                logger.error(f"GitHub organization '{self.org_name}' not found. Please check your GITHUB_ORG_NAME")
                return []
            else:
                logger.error(f"Get repositories error: {e}")
                return []
        except Exception as e:
            logger.error(f"Get repositories error: {e}")
            return []
    
    def _get_recent_commits(self, repo_name: str, days: int = 7) -> List[Dict]:
        """Get recent commits from a repository."""
        try:
            headers = {
                'Authorization': f'token {self.access_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            since_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            url = f"{self.base_url}/repos/{self.org_name}/{repo_name}/commits"
            params = {
                'since': since_date,
                'per_page': 50
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            commits = []
            for commit in response.json():
                commit_data = {
                    'id': commit['sha'],
                    'message': commit['commit']['message'],
                    'author': commit['commit']['author']['name'],
                    'date': commit['commit']['author']['date'],
                    'repo': repo_name,
                    'source': 'github'
                }
                
                # Add metadata
                metadata = {
                    'repo_name': repo_name,
                    'author': commit['commit']['author']['name'],
                    'timestamp': commit['commit']['author']['date'],
                    'tags': ['github', 'commit', f'github-{repo_name}']
                }
                
                commit_data['metadata'] = metadata
                commits.append(commit_data)
            
            return commits
            
        except Exception as e:
            logger.error(f"Get commits error: {e}")
            return []
    
    def _get_pull_requests(self, repo_name: str, state: str = 'all') -> List[Dict]:
        """Get pull requests from a repository."""
        try:
            headers = {
                'Authorization': f'token {self.access_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            url = f"{self.base_url}/repos/{self.org_name}/{repo_name}/pulls"
            params = {
                'state': state,
                'per_page': 50
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            prs = []
            for pr in response.json():
                pr_data = {
                    'id': pr['number'],
                    'title': pr['title'],
                    'body': pr.get('body', ''),
                    'author': pr['user']['login'],
                    'state': pr['state'],
                    'created_at': pr['created_at'],
                    'updated_at': pr['updated_at'],
                    'repo': repo_name,
                    'source': 'github'
                }
                
                # Add metadata
                metadata = {
                    'repo_name': repo_name,
                    'author': pr['user']['login'],
                    'state': pr['state'],
                    'created_at': pr['created_at'],
                    'tags': ['github', 'pull_request', f'github-{repo_name}']
                }
                
                pr_data['metadata'] = metadata
                prs.append(pr_data)
            
            return prs
            
        except Exception as e:
            logger.error(f"Get pull requests error: {e}")
            return []
    
    def _get_issues(self, repo_name: str, state: str = 'all') -> List[Dict]:
        """Get issues from a repository."""
        try:
            headers = {
                'Authorization': f'token {self.access_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            url = f"{self.base_url}/repos/{self.org_name}/{repo_name}/issues"
            params = {
                'state': state,
                'per_page': 50
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            issues = []
            for issue in response.json():
                # Skip pull requests (they're also returned by the issues endpoint)
                if 'pull_request' in issue:
                    continue
                
                issue_data = {
                    'id': issue['number'],
                    'title': issue['title'],
                    'body': issue.get('body', ''),
                    'author': issue['user']['login'],
                    'state': issue['state'],
                    'labels': [label['name'] for label in issue.get('labels', [])],
                    'created_at': issue['created_at'],
                    'updated_at': issue['updated_at'],
                    'repo': repo_name,
                    'source': 'github'
                }
                
                # Add metadata
                metadata = {
                    'repo_name': repo_name,
                    'author': issue['user']['login'],
                    'state': issue['state'],
                    'labels': [label['name'] for label in issue.get('labels', [])],
                    'created_at': issue['created_at'],
                    'tags': ['github', 'issue', f'github-{repo_name}']
                }
                
                issue_data['metadata'] = metadata
                issues.append(issue_data)
            
            return issues
            
        except Exception as e:
            logger.error(f"Get issues error: {e}")
            return []
