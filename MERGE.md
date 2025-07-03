# RAG PDF Upload Feature - Merge and Deployment Guide

## 🚀 Feature Overview
This feature adds RAG (Retrieval-Augmented Generation) functionality to the Asimov-Vedanta Interface, allowing users to:
- Upload PDF documents
- Chat with document content using AI
- Switch between general chat and document-specific chat modes
- Manage multiple document sessions

## 📋 Pre-Deployment Checklist

### 1. Environment Variables
Before deploying to Vercel, you need to set up environment variables:

**In Vercel Dashboard:**
1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add: `OPENAI_API_KEY` = your OpenAI API key

### 2. File Size Limits
- Vercel has a 4.5MB limit for serverless functions
- PDF uploads are limited by this constraint
- Consider chunking large PDFs or using external storage for production

### 3. Storage Considerations
- Vector databases are stored in `/tmp` on Vercel (ephemeral)
- Sessions will be lost on function cold starts
- For production, consider using a persistent database (e.g., Pinecone, Weaviate)

## 🔄 Merge Instructions

### GitHub PR Route:
1. Push your feature branch:
   ```bash
   git push origin feature/rag-pdf-upload
   ```
2. Create a Pull Request on GitHub
3. Review the changes
4. Merge to main branch

### GitHub CLI Route:
```bash
# Create PR
gh pr create --title "Add RAG PDF Upload Functionality" --body "Implements PDF upload and chat with documents using RAG pipeline"

# Review and merge
gh pr review --approve
gh pr merge --squash
```

## 🚀 Deployment Steps

### 1. Deploy to Vercel
```bash
# Install Vercel CLI if not already installed
npm install -g vercel

# Deploy
vercel --prod
```

### 2. Set Environment Variables in Vercel
```bash
vercel env add OPENAI_API_KEY
# Enter your OpenAI API key when prompted
```

### 3. Verify Deployment
- Check that the API endpoints work: `/api/health`
- Test PDF upload functionality
- Verify RAG chat works correctly

## 📁 New Files Added
- `api/rag_service.py` - RAG service implementation
- `aimakerspace/` - AI utilities library
- Updated `api/app.py` - New RAG endpoints
- Updated `frontend/src/app/page.tsx` - PDF upload UI

## 🔧 API Endpoints
- `POST /api/rag/upload` - Upload PDF files
- `POST /api/rag/chat` - Chat with documents
- `GET /api/rag/sessions` - List sessions
- `DELETE /api/rag/sessions/{session_id}` - Delete session

## ⚠️ Important Notes
1. **Temporary Storage**: Vector databases are stored in `/tmp` and will be lost on cold starts
2. **File Size Limits**: Vercel has 4.5MB function size limits
3. **API Key Security**: Ensure OPENAI_API_KEY is set in Vercel environment variables
4. **CORS**: Updated CORS headers to support DELETE method

## 🐛 Troubleshooting
- If PDF upload fails, check file size limits
- If RAG chat doesn't work, verify OPENAI_API_KEY is set
- If sessions disappear, this is expected behavior on Vercel (use persistent storage for production)

## 🔮 Future Improvements
- Add persistent vector database (Pinecone, Weaviate)
- Implement file size optimization
- Add support for more document types
- Add user authentication and session management 