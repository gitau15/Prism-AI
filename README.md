# Prism AI

Prism AI is an intelligent document query system that uses Retrieval-Augmented Generation (RAG) to provide accurate answers based on your documents.

## Features

- **User Authentication & Management**: Secure user identification and API key management
- **Cloud Storage Integration**: Connect to Google Drive, SharePoint, and other providers
- **Document Processing Pipeline**: Parse, chunk, embed, and store documents
- **Intelligent Query System**: RAG-based question answering using your documents
- **Multiple LLM Support**: Works with Gemini, GLM, and Mistral models
- **Vector Database**: Uses ChromaDB for efficient similarity search

## Architecture

Prism AI follows a modular architecture:

1. **API Layer** (FastAPI): RESTful endpoints for all functionality
2. **Core Services**: 
   - Authentication & User Management
   - Document Processing Pipeline
   - Cloud Storage Connectors
   - Query Processing Engine
3. **Data Layer**:
   - SQL Database (SQLite/PostgreSQL) for user and document metadata
   - Vector Database (ChromaDB) for embeddings
4. **External Integrations**:
   - LLM Providers (Gemini, GLM, Mistral)
   - Cloud Storage APIs (Google Drive, SharePoint)
   - Payment Processing (Daraja API)

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables in `.env` file
4. Run the application:
   ```bash
   python startup.py
   ```

## API Endpoints

- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{user_id}` - Get user details
- `GET /api/v1/storage/providers` - List storage providers
- `GET /api/v1/storage/{provider}/files` - List files in storage
- `POST /api/v1/documents/` - Upload document
- `POST /api/v1/documents/{document_id}/process` - Process document
- `POST /api/v1/query/ask` - Ask questions about documents

## Development

Prism AI is built with:
- FastAPI for the web framework
- SQLAlchemy for ORM
- ChromaDB for vector storage
- Hugging Face Sentence Transformers for embeddings
- Various LLM providers for generation