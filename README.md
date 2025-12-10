# Prism AI - Your Personal Research Assistant

Prism AI is an intelligent document query system that uses Retrieval-Augmented Generation (RAG) to provide accurate answers based on your documents. Simply upload your documents and ask questions - Prism AI will find the relevant information and provide concise answers with sources.

## How It Works

1. **Upload Documents**: Connect your documents (PDF, DOCX, PPTX) to Prism AI
2. **Automatic Processing**: Our system parses, chunks, and indexes your documents in the background
3. **Ask Questions**: Query your documents using natural language
4. **Get Answers**: Receive concise, accurate answers with sources from your documents
## Key Features

- **Simple Document Upload**: Upload PDF, DOCX, and PPTX files with ease
- **Smart Question Answering**: Get accurate answers from your documents using advanced AI
- **Source Citations**: Every answer includes references to the relevant sections in your documents
- **Secure & Private**: Your documents are processed securely and never shared with third parties
- **Mobile Payments**: Upgrade to Pro tier using M-Pesa for higher usage limits
- **Usage-Based Pricing**: Affordable subscription tiers to fit your needs## Architecture

Prism AI follows a modular architecture:

1. **API Layer** (FastAPI): RESTful endpoints for all functionality
2. **Core Services**: 
   - Authentication & User Management
   - Document Processing Pipeline
   - Cloud Storage Connectors
   - Query Processing Engine
   - Usage Tracking & Limit Enforcement
   - Payment Processing
3. **Data Layer**:
   - SQL Database (SQLite/PostgreSQL) for user and document metadata
   - Vector Database (ChromaDB) for embeddings
4. **Background Processing**:
   - Celery workers for asynchronous document processing
   - Redis as message broker and result backend
5. **External Integrations**:
   - LLM Providers (Gemini, GLM, Mistral)
   - Cloud Storage APIs (Google Drive, SharePoint)
   - Payment Processing (Daraja API)

## Getting Started

Prism AI is easy to set up and run locally:

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables in `.env` file
4. Run database migrations:
   ```bash
   alembic upgrade head
   ```
5. Run the application using Docker Compose (recommended):
   ```bash
   docker-compose up -d
   ```

Once running, access the application at `http://localhost:8000`
## API Endpoints

- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{user_id}` - Get user details
- `POST /api/v1/users/{user_id}/upgrade` - Upgrade user to PRO tier (admin only)
- `GET /api/v1/storage/providers` - List storage providers
- `GET /api/v1/storage/{provider}/files` - List files in storage
- `POST /api/v1/documents/` - Upload document (non-blocking)
- `GET /api/v1/documents/{document_id}` - Get document details
- `GET /api/v1/documents/tasks/{task_id}` - Check document processing status
- `POST /api/v1/query/ask` - Ask questions about documents
- `POST /api/v1/payments/initiate` - Initiate M-Pesa payment
- `POST /api/v1/payments/daraja/callback` - Daraja API callback endpoint

## Asynchronous Document Processing

When a user uploads a document, the API immediately accepts the request and returns a task ID. The actual document processing (parsing, chunking, embedding, etc.) happens in the background using Celery workers.

To check the status of a document processing task:
```
GET /api/v1/documents/tasks/{task_id}
```

## Subscription Plans

Prism AI offers two subscription tiers to meet your needs:

### Explorer (Free)
- 50 pages processed per month
- 100 queries per month

### Pro (KES 499/month)
- 500 pages processed per month
- 1000 queries per month
- Priority processing

Upgrade anytime using M-Pesa mobile payments directly from the application.
## Easy Mobile Payments

Upgrading to the Pro plan is simple with our integrated M-Pesa payment system:

1. Click "Upgrade to Pro" in the application
2. Enter your phone number
3. Receive an STK Push prompt on your phone
4. Enter your PIN to complete the payment
5. Enjoy your upgraded Pro features immediately

All payments are securely processed through Safaricom's Daraja API.

## Technical Architecture

Prism AI is built with modern, scalable technologies:

- **FastAPI**: High-performance web framework for the API
- **Celery & Redis**: Asynchronous task processing for document handling
- **ChromaDB**: Vector database for efficient similarity search
- **Hugging Face Sentence Transformers**: State-of-the-art embedding models
- **SQLAlchemy**: Robust database ORM
- **Docker**: Containerized deployment for easy scaling

## Launch Status

Prism AI is ready for public beta! We're looking for early adopters to help us refine the product and provide valuable feedback.

[Live Application](http://localhost:8000) (when running locally)
