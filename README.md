# RAG Demo - Minimal Implementation

A minimal RAG (Retrieval Augmented Generation) implementation for educational purposes, featuring:

- 🤖 AI assistant chat interface
- 🔍 Document search with RAG via tool-calling
- 📚 ChromaDB vector database
- ⚡ FastAPI backend
- 🎨 Simple HTML/CSS/JS frontend
- 🔧 GPT-4.1 Mini integration

**Created by [Davide Pasca](https://github.com/dpasca) at [NEWTYPE K.K.](https://newtypekk.com), Japan**

## Quick Setup

**Option 1: Automated Setup (Recommended)**
```bash
# Linux/Mac
./setup.sh

# Windows
setup.bat
```

**Option 2: Manual Setup**

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

> **Note**: The automated setup script will create the virtual environment, install dependencies, and set up the `.env` file for you. You'll just need to add your OpenAI API key to the `.env` file.

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

**LLM Configuration:**
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_BASE_URL`: API base URL (leave empty for OpenAI, set for other providers)
- `LLM_MODEL`: Language model to use (default: gpt-4.1-mini)

**RAG Configuration:**
- `EMBEDDING_MODEL`: OpenAI embedding model to use (default: text-embedding-3-small)
- `CHUNK_SIZE`: Size of text chunks (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)
- `TOP_K_RESULTS`: Number of chunks to retrieve (default: 5)

**Available models:**
- **LLM Models**: `gpt-4.1-mini`, `gpt-4.1`, or any OpenAI-compatible model
- **Embedding Models**: `text-embedding-3-small`, `text-embedding-3-large`, `text-embedding-ada-002`

**Using with other providers:**
```bash
# For Ollama (local)
OPENAI_BASE_URL=http://localhost:11434/v1
LLM_MODEL=llama2
OPENAI_API_KEY=ollama  # Can be anything for Ollama

# For other OpenAI-compatible APIs
OPENAI_BASE_URL=https://your-provider.com/v1
LLM_MODEL=your-model-name
OPENAI_API_KEY=your-api-key
```

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

## Technical Details

For detailed technical documentation about the RAG implementation, see [TECHNICAL.md](TECHNICAL.md). It covers implementation details, design decisions, and how to extend the system.

## Languages

- [English README](README.md)
- [日本語 README](README_ja.md)
- [Italiano README](README_it.md)
- [English Technical Docs](TECHNICAL.md)
- [日本語技術ドキュメント](TECHNICAL_ja.md)
- [Documentazione Tecnica Italiana](TECHNICAL_it.md)

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