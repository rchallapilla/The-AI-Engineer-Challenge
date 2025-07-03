# PDF RAG Chat System

This application allows users to upload PDF documents and chat with them using AI-powered Retrieval-Augmented Generation (RAG). The system uses the `aimakerspace` library for PDF processing, text chunking, and vector similarity search.

## Features

- 📄 **PDF Upload**: Upload PDF files through a user-friendly interface
- 🔍 **AI Indexing**: Automatically index PDFs using vector embeddings
- 💬 **RAG Chat**: Ask questions about uploaded PDFs and get AI-generated answers
- 🎨 **Modern UI**: Beautiful, responsive interface with dark theme
- ⚡ **Real-time**: Fast response times with streaming capabilities

## Architecture

### Backend (FastAPI)
- **PDF Upload Endpoint**: `/api/upload_pdf` - Accepts PDF files and stores them
- **PDF Chat Endpoint**: `/api/pdf_chat` - Handles RAG-based Q&A
- **Vector Database**: In-memory storage using aimakerspace library
- **Text Processing**: PDF text extraction and chunking

### Frontend (Next.js)
- **PDF Upload Interface**: Drag-and-drop file upload
- **Chat Interface**: Real-time chat with uploaded PDFs
- **Responsive Design**: Works on desktop and mobile devices

## Prerequisites

- Python 3.8+
- Node.js 18+
- OpenAI API key

## Setup Instructions

### 1. Backend Setup

Navigate to the `api` directory and install dependencies:

```bash
cd api
pip install -r requirements.txt
```

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### 2. Frontend Setup

Navigate to the `frontend` directory and install dependencies:

```bash
cd frontend
npm install
```

### 3. Running the Application

#### Backend (Terminal 1)
```bash
cd api
python app.py
```

The backend will start on `http://localhost:8000`

#### Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```

The frontend will start on `http://localhost:3000`

### 4. Testing the System

1. Open your browser and go to `http://localhost:3000`
2. Click on "📄 PDF RAG Chat" to access the PDF chat interface
3. Upload a PDF file using the upload button
4. Wait for the PDF to be indexed (you'll see a success message)
5. Start asking questions about the PDF content

## API Endpoints

### POST `/api/upload_pdf`
Upload a PDF file for indexing.

**Request**: Multipart form data with PDF file
**Response**: 
```json
{
  "filename": "document.pdf",
  "message": "PDF uploaded and indexed successfully.",
  "status": "indexed"
}
```

### POST `/api/pdf_chat`
Chat with an uploaded PDF using RAG.

**Request**:
```json
{
  "question": "What is the main topic of this document?",
  "pdf_filename": "document.pdf",
  "model": "gpt-4o-mini"
}
```

**Response**:
```json
{
  "answer": "Based on the document content...",
  "pdf_filename": "document.pdf",
  "relevant_chunks_used": 3
}
```

## How It Works

1. **PDF Upload**: User uploads a PDF file through the frontend
2. **Text Extraction**: The backend uses `aimakerspace.PDFLoader` to extract text from the PDF
3. **Text Chunking**: Text is split into smaller chunks using `CharacterTextSplitter`
4. **Vector Embeddings**: Each chunk is converted to a vector embedding using OpenAI's embedding model
5. **Vector Database**: Embeddings are stored in an in-memory vector database
6. **RAG Query**: When a user asks a question:
   - The question is converted to a vector embedding
   - Similar chunks are retrieved using cosine similarity
   - Relevant context is combined with the question
   - An AI model generates a response based on the context

## File Structure

```
├── api/
│   ├── app.py                 # FastAPI backend
│   ├── requirements.txt       # Python dependencies
│   ├── test_pdf_rag.py       # Test script
│   ├── pdf_uploads/          # Stored PDF files
│   └── vector_indices/       # Vector database storage
├── frontend/
│   ├── src/app/
│   │   ├── page.tsx          # Main chat interface
│   │   └── pdf-chat/
│   │       └── page.tsx      # PDF RAG chat interface
│   └── package.json
├── aimakerspace/             # Custom RAG library
│   ├── text_utils.py         # PDF loading and text processing
│   ├── vectordatabase.py     # Vector database implementation
│   └── openai_utils/         # OpenAI integration
└── PDF_RAG_README.md         # This file
```

## Testing

Run the test script to verify the aimakerspace library is working:

```bash
cd api
python test_pdf_rag.py
```

## Troubleshooting

### Common Issues

1. **OpenAI API Key Not Set**
   - Ensure `OPENAI_API_KEY` environment variable is set
   - Check that the API key is valid and has sufficient credits

2. **PDF Upload Fails**
   - Verify the file is a valid PDF
   - Check file permissions and disk space
   - Ensure the `pdf_uploads` directory exists

3. **Frontend Can't Connect to Backend**
   - Verify the backend is running on port 8000
   - Check CORS settings in the backend
   - Ensure network connectivity

4. **Vector Database Issues**
   - Check that all dependencies are installed
   - Verify OpenAI API key has embedding model access
   - Run the test script to verify functionality

## Dependencies

### Backend Dependencies
- `fastapi==0.115.12` - Web framework
- `uvicorn==0.34.2` - ASGI server
- `openai==1.77.0` - OpenAI API client
- `pydantic==2.11.4` - Data validation
- `python-multipart==0.0.18` - File upload handling
- `PyPDF2==3.0.1` - PDF text extraction
- `numpy==1.24.3` - Numerical computing
- `python-dotenv==1.0.0` - Environment variable management

### Frontend Dependencies
- `next.js` - React framework
- `react` - UI library
- `typescript` - Type safety

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

This project is part of The AI Engineer Challenge.