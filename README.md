# Internal Assistant Platform

A local-first MVP of an internal AI assistant platform that aggregates and summarizes information from Slack, Outlook, and GitHub.

## Features

- 🔍 **Data Aggregation**: Pulls data from Slack, Outlook, and GitHub
- 📄 **Document Upload**: Upload and process PDF/Word documents for context
- 💬 **Chat Interface**: Ask questions about your aggregated data and documents
- 🔐 **Role-Based Access**: Control what data users can see based on their role
- 🧠 **AI-Powered**: Uses vector search and RAG for intelligent responses
- 🏗️ **Modular Design**: Easy to refactor to Azure Foundry stack later

## Project Structure

```
internal-assistant/
├── frontend/            # Svelte frontend
│   ├── src/
│   └── public/
├── backend/             # Flask backend
│   ├── app.py
│   ├── routes/
│   └── services/
├── data/                # Indexed docs
├── embeddings/          # Vector DB
├── uploads/             # Temporary file storage
├── config/              # Role mappings, integration keys
├── .env
└── README.md
```

## Quick Start

### 1. Install Dependencies
```bash
# Run the automated setup script
./setup-yarn.sh

# This will:
# - Create virtual environment
# - Install Python dependencies
# - Install Node.js dependencies
# - Set up Yarn
```

### 2. Verify Setup (Optional)
```bash
# Check that everything is installed correctly
./check-setup.sh
```

### 3. Configure Environment (Optional)
```bash
# Copy environment template
cp env.example .env

# Edit .env with your API keys (optional for basic functionality)
# At minimum, set OPENAI_API_KEY for AI features
```

### 4. Start the Application
```bash
# Start both frontend and backend services
./start-all.sh

# This starts:
# - Backend (Flask) on http://localhost:5000
# - Frontend (Svelte) on http://localhost:3000
```

### 5. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

### 6. Use the Application
- **Chat**: Ask questions about your data
- **Documents**: Upload PDF/Word documents for additional context
- **Integrations**: Configure Slack, GitHub, or Outlook (in progress)

### 7. Stop the Application
```bash
# Stop all services gracefully
./shutdown-all.sh
```

## Integrations

### Slack Integration [UNTESTED] (Optional)
The platform supports real Slack integration with the following features:
- **Real-time Data**: Pulls actual messages from your Slack workspace
- **Channel Management**: Reads from public channels
- **User Information**: Retrieves user details and message metadata
- **Fallback Support**: Uses mock data when Slack is not configured

**Setup**: See `SLACK_SETUP.md` for detailed instructions or run `./setup_slack.sh`
**Note**: Slack integration is optional - the platform works without it

### Document Upload [TESTED]
The platform supports uploading and processing PDF and Word documents:
- **File Types**: PDF (.pdf), Word (.docx, .doc)
- **Processing**: Text extraction, chunking, and vector embedding
- **Search**: Documents are searchable in the chat interface
- **Management**: View, delete, and bulk manage uploaded documents

**Setup**: No additional setup required - use the Documents page in the UI

### GitHub Integration
- Repository information
- Commit history
- Pull requests and issues

### Outlook Integration
- Email management
- Calendar integration
- Contact information

## Development Phases

- **Phase 1**: ✅ Svelte UI + Backend Routes
- **Phase 2**: 🔄 Slack Integration (Real Data)
- **Phase 3**: ✅ Document Upload & Management
- **Phase 4**: 🔄 GitHub/Outlook Integration (Real Data)
- **Phase 5**: 🔄 Role-Based Access
- **Phase 6**: 🔄 Chat Interface
- **Phase 7**: 🔄 Polish + Documentation

## Tech Stack

- **Frontend**: Svelte + Tailwind CSS
- **Backend**: Flask
- **Vector DB**: local file storage
- **LLM**: OpenAI GPT-4
- **Embeddings**: OpenAI text-embedding-3-small
# UnlimitedAI_InternalAssistant
