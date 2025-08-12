# 📁 Internal Assistant Platform - File Structure

This document provides a complete overview of the project file structure with detailed explanations of each component.

## 🏗️ Project Overview

The Internal Assistant Platform is a local-first MVP that aggregates data from Slack, GitHub, and Outlook, providing a chat interface with role-based access control and vector search capabilities.

## 📂 Complete File Structure

```
internal-assistant/
├── 📄 README.md                           # Main project documentation
├── 📄 FILE_STRUCTURE.md                   # This file - complete structure overview
├── 📄 env.example                         # Environment variables template
├── 📄 .gitignore                          # Git ignore rules
├── 📄 setup.sh                            # Automated setup script
│
├── 🐍 backend/                            # Flask Python Backend
│   ├── 📄 __init__.py                     # Backend package initialization
│   ├── 📄 app.py                          # Main Flask application
│   ├── 📄 requirements.txt                # Python dependencies
│   │
│   ├── 🛣️ routes/                         # API Route Handlers
│   │   ├── 📄 __init__.py                 # Routes package initialization
│   │   ├── 📄 auth.py                     # Authentication endpoints
│   │   │   ├── POST /auth/login           # User login
│   │   │   ├── POST /auth/logout          # User logout
│   │   │   ├── GET /auth/me               # Current user info
│   │   │   └── GET /auth/check            # Auth status check
│   │   │
│   │   ├── 📄 chat.py                     # Chat interface endpoints
│   │   │   ├── POST /chat/send            # Send message to AI
│   │   │   ├── GET /chat/history          # Chat history
│   │   │   └── POST /chat/stream          # Streaming responses
│   │   │
│   │   ├── 📄 integrations.py             # Integration management
│   │   │   ├── GET /integrations/status   # Integration status
│   │   │   ├── POST /integrations/slack/sync    # Sync Slack data
│   │   │   ├── POST /integrations/github/sync   # Sync GitHub data
│   │   │   ├── POST /integrations/outlook/sync  # Sync Outlook data
│   │   │   └── POST /integrations/sync/all      # Sync all integrations
│   │   │
│   │   ├── 📄 documents.py                # Document management endpoints
│   │   │   ├── POST /documents/upload     # Upload and process documents
│   │   │   ├── GET /documents/list        # List uploaded documents
│   │   │   ├── DELETE /documents/delete/<filename>  # Delete document
│   │   │   ├── POST /documents/search     # Search within documents
│   │   │   ├── POST /documents/save       # Save documents to disk
│   │   │   └── POST /documents/replace    # Replace existing document
│   │   │
│   │   └── 📄 data.py                     # Data retrieval endpoints
│   │       ├── GET /data/summary          # Data summary by role
│   │       ├── GET /data/slack            # Slack data filtered by role
│   │       ├── GET /data/github           # GitHub data filtered by role
│   │       ├── GET /data/outlook          # Outlook data filtered by role
│   │       └── GET /data/search           # Cross-platform search
│   │
│   └── 🔧 services/                       # Business Logic Services
│       ├── 📄 __init__.py                 # Services package initialization
│       ├── 📄 llm_service.py              # OpenAI integration for chat
│       │   ├── generate_response()        # Generate AI responses
│       │   ├── get_embeddings()           # Get text embeddings
│       │   └── _create_system_prompt()    # Role-based prompts
│       │
│       ├── 📄 vector_service.py           # Vector search & embeddings
│       │   ├── search()                   # Semantic search
│       │   ├── add_document()             # Add to vector DB
│       │   ├── _cosine_similarity()       # Similarity calculation
│       │   └── _can_access_document()     # Role-based filtering
│       │
│       ├── 📄 slack_service.py            # Slack API integration
│       │   ├── sync_data()                # Sync Slack messages
│       │   ├── _get_channels()            # Get Slack channels
│       │   ├── _get_channel_messages()    # Get channel messages
│       │   ├── get_mentions()             # Get user mentions
│       │   └── get_user_info()            # Get user details
│       │
│       ├── 📄 github_service.py           # GitHub API integration
│       │   ├── sync_data()                # Sync GitHub data
│       │   ├── _get_repositories()        # Get organization repos
│       │   ├── _get_recent_commits()      # Get recent commits
│       │   ├── _get_pull_requests()       # Get pull requests
│       │   └── _get_issues()              # Get issues
│       │
│       ├── 📄 outlook_service.py          # Microsoft Graph API integration
│       │   ├── sync_data()                # Sync Outlook emails
│       │   ├── _get_access_token()        # Get OAuth token
│       │   ├── _get_emails()              # Get emails from folder
│       │   ├── _get_unread_emails()       # Get unread emails
│       │   ├── _get_email_folders()       # Get email folders
│       │   └── mark_email_as_read()       # Mark email as read
│       │
│       ├── 📄 data_service.py             # Data aggregation & filtering
│       │   ├── get_summary()               # Get data summary by role
│       │   ├── get_slack_data()            # Get filtered Slack data
│       │   ├── get_github_data()           # Get filtered GitHub data
│       │   ├── get_outlook_data()          # Get filtered Outlook data
│       │   ├── search_data()               # Cross-platform search
│       │   └── _can_access_source()        # Role-based access control
│       │
│       └── 📄 document_service.py          # Document processing & management
│           ├── process_document()          # Process uploaded documents
│           ├── check_duplicate_file()      # Check for duplicate files
│           ├── replace_document()          # Replace existing documents
│           ├── get_uploaded_documents()    # List uploaded documents
│           ├── delete_document()           # Delete documents
│           ├── _extract_pdf_text()         # Extract text from PDFs
│           ├── _extract_docx_text()        # Extract text from Word docs
│           └── _chunk_text()               # Split text into chunks
│
├── 🎨 frontend/                           # Svelte Frontend Application
│   ├── 📄 package.json                    # Node.js dependencies
│   ├── 📄 vite.config.js                  # Vite configuration with API proxy
│   ├── 📄 svelte.config.js                # Svelte configuration
│   ├── 📄 tailwind.config.js              # Tailwind CSS configuration
│   ├── 📄 postcss.config.js               # PostCSS configuration
│   │
│   └── 📁 src/                            # Source code
│       ├── 📄 app.html                    # Main HTML template
│       ├── 📄 app.css                     # Global styles with Tailwind
│       │
│       └── 🛣️ routes/                     # SvelteKit Routes
│           ├── 📄 +layout.svelte          # Main layout with authentication
│           │   ├── Authentication check    # Check user auth status
│           │   ├── Sidebar navigation     # Navigation menu
│           │   ├── User info display      # Show current user
│           │   └── Logout functionality   # Handle user logout
│           │
│           ├── 📄 +page.svelte            # Dashboard page
│           │   ├── Data summary cards     # Slack, GitHub, Outlook stats
│           │   ├── Sync all button        # Sync all integrations
│           │   ├── Quick actions          # Navigation shortcuts
│           │   └── Loading states         # Loading indicators
│           │
│           ├── 📁 login/                  # Authentication pages
│           │   └── 📄 +page.svelte        # Login form
│           │       ├── Email/password form # Login inputs
│           │       ├── Error handling     # Display login errors
│           │       └── Form validation    # Input validation
│           │
│           ├── 📁 chat/                   # Chat interface
│           │   └── 📄 +page.svelte        # Chat page
│           │       ├── Message display     # Show chat messages
│           │       ├── Message input       # Text input with send
│           │       ├── Source citations    # Show response sources
│           │       ├── Loading indicators  # Typing indicators
│           │       └── Auto-scroll        # Scroll to bottom
│           │
│           ├── 📁 integrations/           # Integration management
│           │   └── 📄 +page.svelte        # Integrations page
│           │       ├── Integration cards   # Slack, GitHub, Outlook status
│           │       ├── Sync buttons        # Individual sync actions
│           │       ├── Sync all button     # Sync all integrations
│           │       └── Configuration info  # Setup instructions
│           │
│           └── 📁 documents/              # Document management
│               └── 📄 +page.svelte        # Documents page
│                   ├── File upload         # Upload PDF/Word documents
│                   ├── Document list       # View uploaded documents
│                   ├── Bulk operations     # Select all, delete selected
│                   ├── Search documents    # Search within documents
│                   └── Progress tracking   # Upload progress indicators
│
├── ⚙️ config/                             # Configuration files
│   └── 📄 roles.json                      # Role-based access control
│       ├── Role definitions               # Admin, developer, marketing, etc.
│       ├── Access permissions             # What each role can access
│       └── User mappings                  # Email to role mappings
│
├── 📊 data/                               # Data storage (created by setup)
│   └── (Indexed documents)               # Processed data files
│
├── 📁 uploads/                            # Temporary file storage
│   └── (Temporary uploads)               # Files during processing
│
└── 🧠 embeddings/                         # Vector database (created by setup)
    ├── documents.json                     # Document metadata
    └── embeddings.json                    # Vector embeddings
```

## 🔧 Key Components Explained

### **Backend Architecture**
- **Flask App**: Main application with CORS, session management, and route registration
- **Route Handlers**: RESTful API endpoints for authentication, chat, integrations, and data
- **Services**: Business logic layer handling API integrations, vector search, and data processing
- **Role-Based Access**: User permissions and data filtering based on roles

### **Frontend Architecture**
- **SvelteKit**: Modern frontend framework with file-based routing
- **Tailwind CSS**: Utility-first CSS framework for responsive design
- **Three-Panel Layout**: Sidebar navigation, center content, chat interface
- **Real-time Updates**: Live data sync and chat functionality

### **Integration Services**
- **Slack**: Message retrieval, channel management, user mentions
- **GitHub**: Repository data, commits, pull requests, issues
- **Outlook**: Email management, folder access, read/unread status

### **AI & Search**
- **OpenAI Integration**: GPT-4 for chat responses, embeddings for search
- **Vector Database**: FAISS/Chroma for semantic search and similarity
- **RAG Pipeline**: Retrieve-Augment-Generate for contextual responses

## 🚀 Development Workflow

1. **Setup**: Run `./setup.sh` to install dependencies
2. **Configuration**: Edit `env.example` → `.env` with API keys
3. **Backend**: `cd backend && python app.py` (runs on :5000)
4. **Frontend**: `cd frontend && npm run dev` (runs on :3000)
5. **Access**: Visit `http://localhost:3000`

## 📋 Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_APP_TOKEN=xapp-your-slack-app-token
SLACK_SIGNING_SECRET=your-slack-signing-secret

# GitHub Configuration
GITHUB_ACCESS_TOKEN=your_github_personal_access_token
GITHUB_ORG_NAME=your_organization_name

# Microsoft Graph (Outlook) Configuration
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
MICROSOFT_TENANT_ID=your_microsoft_tenant_id

# Flask Configuration
FLASK_SECRET_KEY=your_flask_secret_key
FLASK_ENV=development
FLASK_DEBUG=True

# Authentication
AUTH_TYPE=local
ALLOWED_USERS=user1@company.com,user2@company.com

# Server Configuration
BACKEND_PORT=5000
FRONTEND_PORT=3000
```

## 🎯 MVP Features

✅ **Must-Have Features**
- OAuth or simple login
- Slack/GitHub/Outlook data pull
- Tag and embed documents
- Role-based filtering
- Chat interface with RAG
- Svelte frontend layout

⚠️ **Nice-to-Have Features**
- Auto-refresh content
- Manual document upload
- Toggle which integrations are active
- Audit logs (who accessed what)

## 🔄 Future Azure Migration

| Feature | MVP (Local) | Azure Version |
|---------|-------------|---------------|
| Frontend | Svelte | Azure Static Web Apps |
| Backend | Flask | Azure Functions / API Management |
| Vector Store | FAISS/Chroma | Azure Cosmos DB (vector) |
| Embeddings | OpenAI API | Azure OpenAI |
| Auth | Local/Session | Microsoft Entra ID |
| Hosting | Localhost | Azure App Services / Container Apps |

This structure provides a solid foundation for the Internal Assistant Platform MVP with clear separation of concerns, scalable architecture, and easy migration path to Azure Foundry stack.
