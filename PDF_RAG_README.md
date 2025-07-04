# 🚀 PDF RAG Chat System: Your AI-Powered Document Assistant!

Welcome to the coolest PDF chat system you've ever seen! 🤖✨ This bad boy lets you upload PDFs and have meaningful conversations with them using the power of AI and the amazing `aimakerspace` library.

## 🎯 What This Baby Does

- **📄 PDF Upload**: Drag, drop, and watch the magic happen
- **🧠 AI Indexing**: Your PDF gets brainy with vector embeddings
- **💬 Smart Chat**: Ask questions and get intelligent answers based on your document
- **⚡ Lightning Fast**: Real-time responses that'll make your head spin
- **🎨 Beautiful UI**: So pretty you'll want to stare at it all day

## 🏗️ The Tech Stack (The Cool Stuff)

### **Backend (FastAPI)**
- **PDF Upload Endpoint**: `/api/upload_pdf` - Handles your files like a pro
- **RAG Chat Endpoint**: `/api/pdf_chat` - The brain behind the operation
- **Vector Database**: In-memory storage using aimakerspace (because we're fancy)
- **Text Processing**: PDF extraction and smart chunking

### **Frontend (Next.js)**
- **Upload Interface**: Drag-and-drop goodness
- **Chat Interface**: Real-time conversations with your docs
- **Responsive Design**: Works on everything from phones to spaceships

## 🚀 Getting Started (The Fun Part)

### **Prerequisites**
- Python 3.8+ (because we're not savages)
- Node.js 18+ (the cool kids use this)
- OpenAI API key (your golden ticket)

### **Setup Instructions**

#### **1. Backend Setup (The Brain)**
```bash
cd api
pip install -r requirements.txt
```

Set your OpenAI API key (don't forget this part!):
```bash
export OPENAI_API_KEY="your-super-secret-api-key-here"
```

#### **2. Frontend Setup (The Beauty)**
```bash
cd frontend
npm install
```

#### **3. Let's Get This Party Started!**

**Backend (Terminal 1):**
```bash
cd api
python app.py
```
Your backend will be rocking at `http://localhost:8000`

**Frontend (Terminal 2):**
```bash
cd frontend
npm run dev
```
Your frontend will be partying at `http://localhost:3000`

#### **4. Test the Magic**
1. Open your browser and go to `http://localhost:3000`
2. Click that sexy "📄 PDF RAG Chat" button
3. Upload a PDF (any PDF, we're not picky)
4. Watch the indexing magic happen
5. Start asking questions like you're chatting with a genius friend

## 🔧 API Endpoints (For the Nerds)

### **POST `/api/upload_pdf`**
Upload your PDF and watch it get smart.

**Request**: Multipart form data with your PDF
**Response**: 
```json
{
  "filename": "your-awesome-document.pdf",
  "message": "PDF uploaded and indexed successfully.",
  "status": "indexed"
}
```

### **POST `/api/pdf_chat`**
Chat with your PDF like it's your best friend.

**Request**:
```json
{
  "question": "What's the main topic of this document?",
  "pdf_filename": "your-awesome-document.pdf",
  "model": "gpt-4o-mini"
}
```

**Response**:
```json
{
  "answer": "Based on the document content...",
  "pdf_filename": "your-awesome-document.pdf",
  "relevant_chunks_used": 3
}
```

## 🧠 How the Magic Works

1. **PDF Upload**: You upload a PDF, we save it (because we're responsible)
2. **Text Extraction**: We use `aimakerspace.PDFLoader` to get the good stuff out
3. **Smart Chunking**: `CharacterTextSplitter` breaks it into digestible pieces
4. **Vector Magic**: Each chunk becomes a vector embedding (fancy math stuff)
5. **RAG Query**: When you ask a question:
   - We turn your question into a vector
   - Find the most similar chunks
   - Combine them with your question
   - Let AI do its thing and give you an answer

## 📁 File Structure (The Organization)

```
├── api/
│   ├── app.py                 # The brain (FastAPI backend)
│   ├── requirements.txt       # Python dependencies
│   ├── test_pdf_rag.py       # Test script (because we're thorough)
│   ├── pdf_uploads/          # Where your PDFs live
│   └── vector_indices/       # Where the magic happens
├── frontend/
│   ├── src/app/
│   │   ├── page.tsx          # Main chat interface
│   │   └── pdf-chat/
│   │       └── page.tsx      # PDF RAG chat interface
│   └── package.json
├── aimakerspace/             # The secret sauce
│   ├── text_utils.py         # PDF loading and text processing
│   ├── vectordatabase.py     # Vector database (the smart part)
│   └── openai_utils/         # OpenAI integration
└── PDF_RAG_README.md         # This awesome file
```

## 🧪 Testing (Because We're Professionals)

Run this to make sure everything's working:
```bash
cd api
python test_pdf_rag.py
```

If you see a bunch of ✅ checkmarks, you're golden!

## 🐛 Troubleshooting (When Things Go Wrong)

### **"OpenAI API Key Not Set"**
- Check your environment variables
- Make sure your API key is valid and has credits
- Don't forget the `export` part!

### **"PDF Upload Fails"**
- Make sure it's actually a PDF file
- Check file permissions and disk space
- Ensure the `pdf_uploads` directory exists

### **"Frontend Can't Connect to Backend"**
- Make sure both servers are running
- Check the ports (8000 for backend, 3000 for frontend)
- Verify CORS settings (we've got you covered)

### **"Vector Database Issues"**
- Check that all dependencies are installed
- Make sure your OpenAI API key has embedding access
- Run the test script to verify functionality

## 📦 Dependencies (The Building Blocks)

### **Backend Dependencies**
- `fastapi==0.115.12` - Web framework (because we're modern)
- `uvicorn==0.34.2` - ASGI server (the engine)
- `openai==1.77.0` - OpenAI API client (the brain connection)
- `pydantic==2.11.4` - Data validation (because we're careful)
- `python-multipart==0.0.18` - File upload handling
- `PyPDF2==3.0.1` - PDF text extraction (the document reader)
- `numpy==1.24.3` - Numerical computing (the math magic)
- `python-dotenv==1.0.0` - Environment variable management

### **Frontend Dependencies**
- `next.js` - React framework (the UI powerhouse)
- `react` - UI library (the building blocks)
- `typescript` - Type safety (because we're responsible)

## 🎯 Pro Tips (From the Experts)

1. **Start Small**: Try with a simple PDF first
2. **Monitor Logs**: Keep an eye on your backend logs
3. **Test Thoroughly**: Upload different types of PDFs
4. **Backup**: Keep local copies of important PDFs
5. **Scale Gradually**: Start with free tiers, upgrade as needed

## 🆘 Need Help? (We've Got Your Back)

- **Backend Issues**: Check your deployment platform's logs
- **Frontend Issues**: Check Vercel's deployment logs
- **API Issues**: Test your backend endpoints directly
- **PDF Issues**: Try with a simple text-based PDF first

## 🎉 You're Ready to Rock!

Your PDF RAG system is now ready to handle any document you throw at it. Upload PDFs, ask questions, and watch the AI magic happen! 

**Remember**: This isn't just a tool, it's your AI-powered document assistant. Treat it well, and it'll treat you well! 🚀✨

---

*Built with ❤️ and the power of the `aimakerspace` library* 