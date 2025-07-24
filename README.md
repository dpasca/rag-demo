# RAG Demo - Educational Implementation

A minimal RAG (Retrieval Augmented Generation) implementation for educational purposes, featuring:

- 🤖 AI assistant chat interface
- 🔍 Document search with RAG via tool-calling
- 📚 ChromaDB vector database
- ⚡ FastAPI backend
- 🎨 Simple HTML/CSS/JS frontend
- 🔧 GPT-4.1-mini integration

## Setup

1. **Create and activate a virtual environment:**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Linux/Mac:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Copy `.env.example` to `.env` and add your OpenAI API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

4. **Initialize the RAG database:**
   ```bash
   python update_rag.py
   ```

5. **Start the server:**
   ```bash
   python main.py
   ```

6. **Open your browser:**
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

## Development

### Alternative Setup with uv (Advanced)
For faster dependency management, you can use [uv](https://github.com/astral-sh/uv):
```bash
# Install uv if you haven't already
pip install uv

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -r requirements.txt
```