import os
import pickle
import tempfile
import uuid
from typing import List, Dict, Optional
from pathlib import Path

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from aimakerspace.text_utils import PDFLoader, CharacterTextSplitter
from aimakerspace.vectordatabase import VectorDatabase
from aimakerspace.openai_utils.embedding import EmbeddingModel


class RAGService:
    def __init__(self, storage_dir: str = "vector_storage"):
        """
        Initialize RAG service with persistent storage.
        
        Args:
            storage_dir: Directory to store vector databases and metadata
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.embedding_model = EmbeddingModel()
        self.active_sessions: Dict[str, Dict] = {}
        
    def _get_session_file(self, session_id: str) -> Path:
        """Get the file path for a session's vector database."""
        return self.storage_dir / f"session_{session_id}.pkl"
    
    def _get_metadata_file(self, session_id: str) -> Path:
        """Get the file path for a session's metadata."""
        return self.storage_dir / f"metadata_{session_id}.pkl"
    
    def create_session(self) -> str:
        """Create a new session and return its ID."""
        session_id = str(uuid.uuid4())
        self.active_sessions[session_id] = {
            "vector_db": VectorDatabase(self.embedding_model),
            "chunks": [],
            "original_text": "",
            "filename": ""
        }
        return session_id
    
    def process_pdf(self, pdf_file_path: str, session_id: str, filename: str) -> Dict:
        """
        Process a PDF file and index it for RAG.
        
        Args:
            pdf_file_path: Path to the uploaded PDF file
            session_id: Session ID to associate with this PDF
            filename: Original filename
            
        Returns:
            Dict with processing results
        """
        try:
            # Load and extract text from PDF
            pdf_loader = PDFLoader(pdf_file_path)
            documents = pdf_loader.load_documents()
            
            if not documents:
                raise ValueError("No text could be extracted from the PDF")
            
            # Split text into chunks
            splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = splitter.split_texts(documents)
            
            # Get or create session
            if session_id not in self.active_sessions:
                self.active_sessions[session_id] = {
                    "vector_db": VectorDatabase(self.embedding_model),
                    "chunks": [],
                    "original_text": "",
                    "filename": ""
                }
            
            # Update session with new data
            session = self.active_sessions[session_id]
            session["chunks"] = chunks
            session["original_text"] = documents[0] if documents else ""
            session["filename"] = filename
            
            # Index chunks in vector database
            import asyncio
            asyncio.run(session["vector_db"].abuild_from_list(chunks))
            
            # Save to persistent storage
            self._save_session(session_id)
            
            return {
                "success": True,
                "chunks_count": len(chunks),
                "filename": filename,
                "session_id": session_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def query_pdf(self, session_id: str, query: str, k: int = 3) -> Dict:
        """
        Query the indexed PDF using RAG.
        
        Args:
            session_id: Session ID to query
            query: User's question
            k: Number of relevant chunks to retrieve
            
        Returns:
            Dict with query results
        """
        try:
            # Load session if not in memory
            if session_id not in self.active_sessions:
                self._load_session(session_id)
            
            if session_id not in self.active_sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.active_sessions[session_id]
            vector_db = session["vector_db"]
            
            # Search for relevant chunks
            relevant_chunks = vector_db.search_by_text(query, k=k, return_as_text=True)
            
            # Create context from relevant chunks
            context = "\n\n".join(relevant_chunks)
            
            return {
                "success": True,
                "context": context,
                "relevant_chunks": relevant_chunks,
                "filename": session["filename"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _save_session(self, session_id: str):
        """Save session data to persistent storage."""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        
        # Save vector database
        with open(self._get_session_file(session_id), 'wb') as f:
            pickle.dump(session["vector_db"], f)
        
        # Save metadata
        metadata = {
            "chunks": session["chunks"],
            "original_text": session["original_text"],
            "filename": session["filename"]
        }
        with open(self._get_metadata_file(session_id), 'wb') as f:
            pickle.dump(metadata, f)
    
    def _load_session(self, session_id: str):
        """Load session data from persistent storage."""
        session_file = self._get_session_file(session_id)
        metadata_file = self._get_metadata_file(session_id)
        
        if not session_file.exists() or not metadata_file.exists():
            return
        
        try:
            # Load vector database
            with open(session_file, 'rb') as f:
                vector_db = pickle.load(f)
            
            # Load metadata
            with open(metadata_file, 'rb') as f:
                metadata = pickle.load(f)
            
            # Reconstruct session
            self.active_sessions[session_id] = {
                "vector_db": vector_db,
                "chunks": metadata["chunks"],
                "original_text": metadata["original_text"],
                "filename": metadata["filename"]
            }
            
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
    
    def list_sessions(self) -> List[Dict]:
        """List all available sessions."""
        sessions = []
        for metadata_file in self.storage_dir.glob("metadata_*.pkl"):
            session_id = metadata_file.stem.replace("metadata_", "")
            try:
                with open(metadata_file, 'rb') as f:
                    metadata = pickle.load(f)
                sessions.append({
                    "session_id": session_id,
                    "filename": metadata.get("filename", "Unknown"),
                    "chunks_count": len(metadata.get("chunks", []))
                })
            except Exception as e:
                print(f"Error loading session metadata for {session_id}: {e}")
        
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and its associated files."""
        try:
            # Remove from memory
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            # Remove files
            session_file = self._get_session_file(session_id)
            metadata_file = self._get_metadata_file(session_id)
            
            if session_file.exists():
                session_file.unlink()
            if metadata_file.exists():
                metadata_file.unlink()
            
            return True
            
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False 