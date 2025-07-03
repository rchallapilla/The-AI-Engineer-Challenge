# Import required FastAPI components for building the API
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware
# Import Pydantic for data validation and settings management
from pydantic import BaseModel
# Import OpenAI client for interacting with OpenAI's API
from openai import OpenAI
import os
from typing import Optional
import shutil
import sys

# Add the parent directory to the path to import aimakerspace
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import aimakerspace components for PDF processing and RAG
from aimakerspace.text_utils import PDFLoader, CharacterTextSplitter
from aimakerspace.vectordatabase import VectorDatabase
from aimakerspace.openai_utils.chatmodel import ChatOpenAI

# Initialize FastAPI application with a title
app = FastAPI(title="OpenAI Chat API")

# Get OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Configure CORS (Cross-Origin Resource Sharing) middleware
# This allows the API to be accessed from different domains/origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://asimov-vedanta-12lxb8yaj-raghus-projects-920446ba.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Define the data model for chat requests using Pydantic
# This ensures incoming request data is properly validated
class ChatRequest(BaseModel):
    developer_message: str  # Message from the developer/system
    user_message: str      # Message from the user
    model: Optional[str] = "gpt-4.1-mini"  # Optional model selection with default

# Directory to store uploaded PDFs and vector indices
PDF_UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'pdf_uploads')
VECTOR_INDEX_DIR = os.path.join(os.path.dirname(__file__), 'vector_indices')
os.makedirs(PDF_UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTOR_INDEX_DIR, exist_ok=True)

# Global variable to store vector databases for uploaded PDFs
pdf_vector_dbs = {}

# Define the main chat endpoint that handles POST requests
@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # Initialize OpenAI client with the environment variable API key
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Create an async generator function for streaming responses
        async def generate():
            # Create a streaming chat completion request
            stream = client.chat.completions.create(
                model=request.model,
                messages=[
                    {"role": "developer", "content": request.developer_message},
                    {"role": "user", "content": request.user_message}
                ],
                stream=True  # Enable streaming response
            )
            
            # Yield each chunk of the response as it becomes available
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        # Return a streaming response to the client
        return StreamingResponse(generate(), media_type="text/plain", headers={
            "Access-Control-Allow-Origin": "https://asimov-vedanta-12lxb8yaj-raghus-projects-920446ba.vercel.app",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        })
    
    except Exception as e:
        # Handle any errors that occur during processing
        raise HTTPException(status_code=500, detail=str(e))

# Define a health check endpoint to verify API status
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

@app.post("/api/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Endpoint to upload a PDF file, save it to disk, and index it using aimakerspace.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    file_path = os.path.join(PDF_UPLOAD_DIR, file.filename)
    
    try:
        # Save the uploaded PDF
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Index the PDF using aimakerspace
        await index_pdf(file_path, file.filename)
        
        return {
            "filename": file.filename, 
            "message": "PDF uploaded and indexed successfully.",
            "status": "indexed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

async def index_pdf(file_path: str, filename: str):
    """
    Index a PDF file using aimakerspace components.
    """
    try:
        # Load PDF content using aimakerspace PDFLoader
        pdf_loader = PDFLoader(file_path)
        documents = pdf_loader.load_documents()
        
        # Split documents into chunks using CharacterTextSplitter
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_texts(documents)
        
        # Create vector database and build embeddings
        vector_db = VectorDatabase()
        await vector_db.abuild_from_list(chunks)
        
        # Store the vector database for this PDF
        pdf_vector_dbs[filename] = {
            'vector_db': vector_db,
            'chunks': chunks,
            'file_path': file_path
        }
        
        print(f"Successfully indexed PDF: {filename} with {len(chunks)} chunks")
        
    except Exception as e:
        print(f"Error indexing PDF {filename}: {str(e)}")
        raise e

# Define the data model for PDF chat requests
class PDFChatRequest(BaseModel):
    question: str
    pdf_filename: str
    model: Optional[str] = "gpt-4o-mini"

@app.post("/api/pdf_chat")
async def pdf_chat(request: PDFChatRequest):
    """
    Endpoint to chat with an uploaded PDF using RAG (Retrieval-Augmented Generation).
    """
    try:
        # Check if the PDF has been indexed
        if request.pdf_filename not in pdf_vector_dbs:
            raise HTTPException(
                status_code=404, 
                detail=f"PDF '{request.pdf_filename}' not found or not indexed. Please upload it first."
            )
        
        pdf_data = pdf_vector_dbs[request.pdf_filename]
        vector_db = pdf_data['vector_db']
        chunks = pdf_data['chunks']
        
        # Retrieve relevant chunks using vector similarity search
        relevant_chunks = vector_db.search_by_text(
            request.question, 
            k=3, 
            return_as_text=True
        )
        
        # Combine relevant chunks into context
        context = "\n\n".join(relevant_chunks)
        
        # Create RAG prompt
        rag_prompt = f"""You are a helpful assistant that answers questions based on the provided context from a PDF document.

Context from the PDF:
{context}

Question: {request.question}

Please answer the question based on the context provided. If the context doesn't contain enough information to answer the question, say so. Keep your answer concise and relevant."""

        # Initialize chat model and get response
        chat_model = ChatOpenAI(model_name=request.model)
        response = chat_model.run([
            {"role": "user", "content": rag_prompt}
        ])
        
        return {
            "answer": response,
            "pdf_filename": request.pdf_filename,
            "relevant_chunks_used": len(relevant_chunks)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

# Entry point for running the application directly
if __name__ == "__main__":
    import uvicorn
    # Start the server on all network interfaces (0.0.0.0) on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
