# Slack Integration Setup Guide

This guide will help you set up real Slack integration for the Internal Assistant platform.

## Prerequisites

1. **Slack Workspace**: You need admin access to a Slack workspace
2. **Slack App**: You'll need to create a Slack app in your workspace
3. **Environment Variables**: You'll need to configure the required environment variables

## Step 1: Create a Slack App

### 1.1 Go to Slack API Console
1. Visit [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App"
3. Choose "From scratch"
4. Enter app name (e.g., "Internal Assistant")
5. Select your workspace

### 1.2 Configure App Permissions

#### Bot Token Scopes
Navigate to "OAuth & Permissions" and add these scopes:

**Required Scopes:**
- `channels:read` - Read public channels
- `channels:history` - Read channel messages
- `users:read` - Read user information
- `users:read.email` - Read user email addresses

**Optional Scopes (for enhanced features):**
- `groups:read` - Read private channels (if needed)
- `groups:history` - Read private channel messages
- `im:read` - Read direct messages
- `im:history` - Read direct message history

### 1.3 Install App to Workspace
1. Go to "Install App" in the sidebar
2. Click "Install to Workspace"
3. Authorize the app

### 1.4 Get Your Credentials
After installation, you'll get:
- **Bot User OAuth Token** (starts with `xoxb-`)
- **Signing Secret** (found in "Basic Information" → "App Credentials")

## Step 2: Configure Environment Variables

Create a `.env` file in the `internal-assistant` directory with your Slack credentials:

```bash
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here
```

### 2.1 Get Your App Token
1. Go to "Basic Information" in your Slack app
2. Scroll to "App-Level Tokens"
3. Click "Generate Token and Scopes"
4. Add the `connections:write` scope
5. Copy the token (starts with `xapp-`)

## Step 3: Test the Integration

### 3.1 Start the Backend
```bash
cd internal-assistant
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
cd backend
python app.py
```

### 3.2 Test Slack Connection
1. Open your browser to `http://localhost:5000/integrations/status`
2. Check if Slack shows as "connected"
3. If not connected, verify your environment variables

### 3.3 Sync Slack Data
1. Send a POST request to `http://localhost:5000/integrations/slack/sync`
2. Or use the frontend interface at `http://localhost:3000/integrations`

## Step 4: Verify Data Flow

### 4.1 Check Data Endpoints
- `GET /data/summary` - Should show real Slack message counts
- `GET /data/slack` - Should return real Slack messages
- `GET /integrations/status` - Should show Slack as connected

### 4.2 Frontend Integration
1. Start the frontend: `cd frontend && npm install && npm run dev`
2. Navigate to `http://localhost:3000`
3. Check the integrations page for Slack status
4. Try syncing data from the UI

## Troubleshooting

### Common Issues

#### 1. "Slack not configured" Error
- Check that all environment variables are set correctly
- Verify the `.env` file is in the correct location
- Restart the backend after changing environment variables

#### 2. "Invalid token" Error
- Verify your bot token starts with `xoxb-`
- Ensure the app is installed to your workspace
- Check that the required scopes are added

#### 3. "No channels found" Error
- Make sure your bot has been added to channels
- Check that the bot has the `channels:read` scope
- Verify the workspace has public channels

#### 4. "Rate limited" Error
- Slack has rate limits (50 requests per second)
- The app includes basic rate limiting, but you may need to implement more sophisticated handling for high-volume usage

### Debug Mode
Enable debug logging by setting:
```bash
FLASK_DEBUG=True
```

## Security Considerations

### 1. Token Security
- Never commit your `.env` file to version control
- Use environment variables in production
- Rotate tokens regularly

### 2. Data Privacy
- The app only reads public channel messages by default
- Private channels require additional scopes and explicit invitation
- User data is processed locally and not stored permanently

### 3. Workspace Permissions
- Only install the app in workspaces you trust
- Review the app's permissions regularly
- Consider using a dedicated workspace for testing

## Advanced Configuration

### Custom Channel Filtering
You can modify the `slack_service.py` to:
- Filter specific channels
- Exclude certain message types
- Add custom message processing

### Rate Limiting
For high-volume workspaces, consider:
- Implementing more sophisticated rate limiting
- Caching channel lists
- Using pagination for large message histories

### Real-time Updates
For real-time message updates, you can:
- Implement Slack Events API
- Use Socket Mode for real-time connections
- Add webhook endpoints for message notifications

## Support

If you encounter issues:
1. Check the backend logs for detailed error messages
2. Verify your Slack app configuration
3. Test with a simple Slack API call using curl
4. Review the Slack API documentation for the latest changes

## Next Steps

Once Slack integration is working:
1. Set up GitHub integration
2. Configure Outlook integration
3. Test the chat interface with real data
4. Implement vector search for Slack messages
5. Add role-based access controls for different channels
