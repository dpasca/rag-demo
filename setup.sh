#!/bin/bash

# RAG Demo Setup Script
# This script sets up the virtual environment and installs dependencies

set -e  # Exit on any error

echo "🚀 Setting up RAG Demo..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Error: Python is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "✅ Found Python: $($PYTHON_CMD --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
$PYTHON_CMD -m venv venv

# Detect OS and set activation command
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    ACTIVATE_CMD="venv\\Scripts\\activate"
    echo "🔧 Detected Windows environment"
else
    ACTIVATE_CMD="source venv/bin/activate"
    echo "🔧 Detected Unix-like environment"
fi

# Activate virtual environment and install dependencies
echo "📥 Installing dependencies..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    cmd //c "venv\\Scripts\\activate && pip install -r requirements.txt"
else
    source venv/bin/activate && pip install -r requirements.txt
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Setting up environment file..."
    cp .env.example .env
    echo "📝 Created .env file from .env.example"
    echo "   Please edit .env and add your OpenAI API key!"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OpenAI API key"
echo "2. Activate the virtual environment:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "   venv\\Scripts\\activate"
else
    echo "   source venv/bin/activate"
fi
echo "3. Initialize the RAG database: python update_rag.py"
echo "4. Start the server: python main.py"
echo "5. Open http://localhost:8000 in your browser"
echo ""
echo "Happy coding! 🤖"