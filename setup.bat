@echo off
REM RAG Demo Setup Script for Windows
REM This script sets up the virtual environment and installs dependencies

echo 🚀 Setting up RAG Demo...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Found Python: %PYTHON_VERSION%

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ❌ Error creating virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment and install dependencies
echo 📥 Installing dependencies...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Error activating virtual environment
    pause
    exit /b 1
)

pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error installing dependencies
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo ⚙️  Setting up environment file...
    copy .env.example .env >nul
    echo 📝 Created .env file from .env.example
    echo    Please edit .env and add your OpenAI API key!
) else (
    echo ✅ .env file already exists
)

echo.
echo 🎉 Setup complete!
echo.
echo Next steps:
echo 1. Edit .env and add your OpenAI API key
echo 2. Activate the virtual environment: venv\Scripts\activate
echo 3. Initialize the RAG database: python update_rag.py
echo 4. Start the server: python main.py
echo 5. Open http://localhost:8000 in your browser
echo.
echo Happy coding! 🤖
pause