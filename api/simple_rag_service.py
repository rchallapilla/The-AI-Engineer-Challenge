import os
import pickle
import tempfile
import uuid
from typing import List, Dict, Optional
from pathlib import Path
import PyPDF2
import numpy as np
from openai import OpenAI

class SimpleRAGService:
    def __init__(self, storage_dir: str = "vector_storage"):
        """
        Initialize simple RAG service with persistent storage.
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.client = OpenAI()
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
            "chunks": [],
            "original_text": "",
            "filename": ""
        }
        return session_id
    
    def extract_text_from_pdf(self, pdf_file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            with open(pdf_file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            raise ValueError(f"Error processing PDF: {str(e)}")
    
    def split_text_into_chunks(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """Split text into chunks."""
        chunks = []
        for i in range(0, len(text), chunk_size - chunk_overlap):
            chunks.append(text[i : i + chunk_size])
        return chunks
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI."""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise ValueError(f"Error getting embedding: {str(e)}")
    
    def cosine_similarity(self, vector_a: List[float], vector_b: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        a = np.array(vector_a)
        b = np.array(vector_b)
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        return dot_product / (norm_a * norm_b)
    
    def process_pdf(self, pdf_file_path: str, session_id: str, filename: str) -> Dict:
        """
        Process a PDF file and index it for RAG.
        """
        try:
            # Extract text from PDF
            text = self.extract_text_from_pdf(pdf_file_path)
            
            if not text.strip():
                raise ValueError("No text could be extracted from the PDF")
            
            # Split text into chunks
            chunks = self.split_text_into_chunks(text)
            
            # Get or create session
            if session_id not in self.active_sessions:
                self.active_sessions[session_id] = {
                    "chunks": [],
                    "original_text": "",
                    "filename": ""
                }
            
            # Update session with new data
            session = self.active_sessions[session_id]
            session["chunks"] = chunks
            session["original_text"] = text
            session["filename"] = filename
            
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
        """
        try:
            # Load session if not in memory
            if session_id not in self.active_sessions:
                self._load_session(session_id)
            
            if session_id not in self.active_sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.active_sessions[session_id]
            chunks = session["chunks"]
            
            if not chunks:
                raise ValueError("No chunks available for this session")
            
            # Get query embedding
            query_embedding = self.get_embedding(query)
            
            # Get embeddings for chunks and compute similarities
            chunk_similarities = []
            for i, chunk in enumerate(chunks):
                try:
                    chunk_embedding = self.get_embedding(chunk)
                    similarity = self.cosine_similarity(query_embedding, chunk_embedding)
                    chunk_similarities.append((chunk, similarity))
                except Exception as e:
                    print(f"Error processing chunk {i}: {e}")
                    continue
            
            # Sort by similarity and get top k
            chunk_similarities.sort(key=lambda x: x[1], reverse=True)
            relevant_chunks = [chunk for chunk, _ in chunk_similarities[:k]]
            
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
        metadata_file = self._get_metadata_file(session_id)
        
        if not metadata_file.exists():
            return
        
        try:
            # Load metadata
            with open(metadata_file, 'rb') as f:
                metadata = pickle.load(f)
            
            # Reconstruct session
            self.active_sessions[session_id] = {
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