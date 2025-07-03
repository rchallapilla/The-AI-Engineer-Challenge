# Import required FastAPI components for building the API
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware
# Import Pydantic for data validation and settings management
from pydantic import BaseModel
# Import OpenAI client for interacting with OpenAI's API
from openai import OpenAI
import os
import tempfile
from typing import Optional, List
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import our simplified RAG service
from simple_rag_service import SimpleRAGService

# Initialize FastAPI application with a title
app = FastAPI(title="OpenAI Chat API with RAG")

# Get OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Initialize simplified RAG service
rag_service = SimpleRAGService()

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

class RAGChatRequest(BaseModel):
    session_id: str
    user_message: str
    model: Optional[str] = "gpt-4.1-mini"

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

# RAG endpoints
@app.post("/api/rag/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file for RAG processing.
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Create a temporary file to store the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Create a new session
        session_id = rag_service.create_session()
        
        # Process the PDF
        result = rag_service.process_pdf(temp_file_path, session_id, file.filename)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "session_id": session_id,
            "filename": file.filename,
            "chunks_count": result["chunks_count"],
            "message": f"PDF '{file.filename}' processed successfully with {result['chunks_count']} chunks"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/api/rag/chat")
async def rag_chat(request: RAGChatRequest):
    """
    Chat with a PDF using RAG.
    """
    try:
        # Get relevant context from the PDF
        rag_result = rag_service.query_pdf(request.session_id, request.user_message)
        
        if not rag_result["success"]:
            raise HTTPException(status_code=500, detail=rag_result["error"])
        
        # Create context-aware prompt
        context = rag_result["context"]
        system_prompt = f"""You are a helpful assistant that answers questions based on the provided document context. 
        
Document Context:
{context}

Please answer the user's question based on the document context above. If the answer cannot be found in the context, say so clearly. 
Keep your answers concise and relevant to the document content."""

        # Initialize OpenAI client
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Create an async generator function for streaming responses
        async def generate():
            # Create a streaming chat completion request
            stream = client.chat.completions.create(
                model=request.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": request.user_message}
                ],
                stream=True
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
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in RAG chat: {str(e)}")

@app.get("/api/rag/sessions")
async def list_sessions():
    """
    List all available RAG sessions.
    """
    try:
        sessions = rag_service.list_sessions()
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")

@app.delete("/api/rag/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a RAG session.
    """
    try:
        success = rag_service.delete_session(session_id)
        if success:
            return {"message": f"Session {session_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")

# Define a health check endpoint to verify API status
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Entry point for running the application directly
if __name__ == "__main__":
    import uvicorn
    # Start the server on all network interfaces (0.0.0.0) on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
