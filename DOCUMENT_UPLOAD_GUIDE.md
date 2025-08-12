# Document Upload Guide

This guide explains how to add context (PDF/Word documents) to your chat assistant.

## Overview

The Internal Assistant now supports uploading PDF and Word documents that will be processed, indexed, and made available as context for the AI chat. Documents are:

- **Text-extracted** from PDF and Word files
- **Chunked** into smaller pieces for better processing
- **Vector-embedded** for semantic search
- **Role-filtered** based on user permissions
- **Searchable** within the chat interface

## How It Works

### 1. Document Processing Pipeline

```
Upload → Text Extraction → Chunking → Embedding → Vector Storage → Search
```

- **PDF Processing**: Uses PyPDF2 to extract text from PDF files
- **Word Processing**: Uses python-docx to extract text from DOCX/DOC files
- **Chunking**: Documents are split into 1000-character chunks with 200-character overlap
- **Embedding**: Each chunk is converted to a vector using OpenAI's text-embedding-3-small
- **Storage**: Vectors are stored in the local FAISS/Chroma database

### 2. Integration with Chat

When you ask a question in the chat:

1. Your question is converted to a vector
2. The system searches for similar document chunks
3. Relevant chunks are retrieved and sent to the LLM
4. The LLM generates a response using the document context

## Usage

### Uploading Documents

1. **Navigate to Documents**: Click "Documents" in the sidebar
2. **Select File**: Choose a PDF or Word document (max 10MB)
3. **Upload**: Click "Upload Document" to process and index
4. **Monitor**: Watch the progress as chunks are created

### Searching Documents

1. **Use the Search Bar**: Enter queries in the document search section
2. **View Results**: See matching document chunks with source information
3. **Chat Integration**: Ask questions in the chat that reference uploaded content

### Managing Documents

- **View All**: See a list of all uploaded documents
- **Delete**: Remove documents you no longer need
- **Chunk Info**: See how many chunks each document was split into

## Supported File Types

- **PDF** (.pdf) - Text extraction from PDF documents
- **Word** (.docx, .doc) - Text extraction from Word documents

## File Limits

- **Size**: Maximum 10MB per file
- **Chunks**: Documents are automatically split into ~1000 character chunks
- **Storage**: Vectors are stored locally in the `embeddings/` directory

## Role-Based Access

Documents follow the same role-based access control as other data:

- **Admin**: Access to all documents
- **Developer**: Access to uploaded documents + GitHub + Slack
- **Marketing**: Access to uploaded documents + Outlook + Slack
- **Sales**: Access to uploaded documents + Outlook + Slack
- **User**: Access to uploaded documents + general Slack

## Technical Details

### Backend Components

- **DocumentService** (`backend/services/document_service.py`): Handles file processing
- **Document Routes** (`backend/routes/documents.py`): API endpoints for upload/management
- **Vector Service** (`backend/services/vector_service.py`): Enhanced for document storage

### Frontend Components

- **Documents Page** (`frontend/src/routes/documents/+page.svelte`): Upload and management interface
- **Navigation** (`frontend/src/routes/+layout.svelte`): Added Documents link

### API Endpoints

- `POST /api/documents/upload` - Upload and process a document
- `GET /api/documents/list` - List all uploaded documents
- `DELETE /api/documents/delete/<filename>` - Delete a document
- `POST /api/documents/search` - Search within documents

## Example Use Cases

### 1. Company Policies
Upload employee handbooks, policy documents, and procedures. Ask questions like:
- "What's our vacation policy?"
- "How do I request time off?"
- "What are the dress code requirements?"

### 2. Technical Documentation
Upload API docs, technical specifications, and user guides. Ask questions like:
- "How do I authenticate with the API?"
- "What are the system requirements?"
- "How do I configure the database?"

### 3. Project Information
Upload project plans, requirements documents, and meeting notes. Ask questions like:
- "What are the current project milestones?"
- "Who is responsible for the frontend?"
- "What was decided in the last meeting?"

## Troubleshooting

### Common Issues

1. **Upload Fails**: Check file size (max 10MB) and format (PDF/DOCX/DOC only)
2. **No Text Found**: Some PDFs may be image-based and won't extract text
3. **Search Not Working**: Ensure OpenAI API key is configured for embeddings
4. **Permission Denied**: Check your user role and document access permissions

### File Processing Tips

- **Text-based PDFs**: Work best for text extraction
- **Scanned PDFs**: May not extract text properly
- **Complex Word Documents**: Tables and images won't be processed
- **Large Files**: Will be split into many chunks for better processing

## Future Enhancements

- **More File Types**: Support for PowerPoint, Excel, and text files
- **Image Processing**: OCR for scanned documents
- **Document Versioning**: Track changes and updates
- **Collaborative Features**: Share documents between users
- **Advanced Search**: Filter by date, author, or document type

## Security Considerations

- **Local Storage**: Documents are stored locally, not in the cloud
- **Role-Based Access**: Users only see documents they have permission for
- **File Validation**: Only allowed file types are processed
- **Size Limits**: Prevents abuse with large file uploads
- **Temporary Files**: Uploaded files are deleted after processing

## Performance Notes

- **Processing Time**: Large documents may take several seconds to process
- **Memory Usage**: Vector storage grows with document count
- **Search Speed**: Vector search is fast but depends on database size
- **Storage**: Each document chunk requires storage for both text and vector

This document upload feature transforms your Internal Assistant from a simple chat interface into a powerful knowledge management system that can reference your organization's documents and provide accurate, contextual responses.
