from http.server import BaseHTTPRequestHandler
import json
import os
import tempfile
import uuid
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Parse request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Extract file data (assuming base64 encoded)
            file_data = request_data.get('file')
            filename = request_data.get('filename', 'document.pdf')
            
            if not file_data:
                raise ValueError("No file data provided")
            
            # Decode base64 file data
            file_bytes = base64.b64decode(file_data)
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(file_bytes)
                temp_file_path = temp_file.name
            
            # Create a session ID
            session_id = str(uuid.uuid4())
            
            # For now, just return success (we'll implement actual PDF processing later)
            # In a real implementation, you'd process the PDF here
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            # Set response headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Send response
            response_data = {
                "success": True,
                "session_id": session_id,
                "filename": filename,
                "chunks_count": 1,  # Placeholder
                "message": f"PDF '{filename}' uploaded successfully"
            }
            self.wfile.write(json.dumps(response_data).encode())
            
        except Exception as e:
            # Handle errors
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_data = {"error": str(e), "success": False}
            self.wfile.write(json.dumps(error_data).encode())
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers() 