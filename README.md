# RAG Demo - Educational Implementation

A minimal RAG (Retrieval Augmented Generation) implementation for educational purposes, featuring:

- 🤖 AI assistant chat interface
- 🔍 Document search with RAG via tool-calling
- 📚 ChromaDB vector database
- ⚡ FastAPI backend
- 🎨 Simple HTML/CSS/JS frontend
- 🔧 GPT-4.1-mini integration

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   - Copy `.env` and add your OpenAI API key:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Initialize the RAG database:**
   ```bash
   python update_rag.py
   ```

4. **Start the server:**
   ```bash
   python main.py
   ```

5. **Open your browser:**
   Navigate to `http://localhost:8000`

## Usage

### Chat Interface
- Ask questions in the web interface
- The AI will automatically search documents when relevant
- Sources are displayed when RAG is used

### Adding Documents
- Place `.txt` files in the `documents/` folder
- Run `python update_rag.py` to update the database
- Documents are chunked with configurable size/overlap

### Configuration
Adjust settings in `.env`:
- `CHUNK_SIZE`: Size of text chunks (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)
- `TOP_K_RESULTS`: Number of chunks to retrieve (default: 5)

## Architecture

```
├── main.py              # FastAPI app
├── chat.py              # Chat logic with OpenAI
├── rag.py               # RAG system with ChromaDB
├── models.py            # Pydantic models
├── update_rag.py        # Document processing script
├── documents/           # Text files for RAG
├── frontend/            # Web interface
│   ├── index.html
│   ├── script.js
│   └── style.css
└── chroma_db/          # Vector database (created automatically)
```

## Key Features

- **Tool-based RAG**: Uses OpenAI function calling to trigger document search
- **Source attribution**: Shows which documents and chunks were used
- **Configurable chunking**: Adjust chunk size and overlap via environment variables
- **Local storage**: ChromaDB runs locally with persistent storage
- **Educational focus**: Clean, readable code with minimal complexity