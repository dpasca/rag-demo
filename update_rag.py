#!/usr/bin/env python3
"""
RAG Update Script

This script updates the RAG database by processing all text documents 
in the 'documents' folder and adding them to ChromaDB.

Usage:
    python update_rag.py
"""

import os
import sys
from rag import rag_system

def main():
    """Update the RAG database with documents from the documents folder."""
    print("RAG Update Script")
    print("=" * 50)
    
    documents_dir = "documents"
    
    if not os.path.exists(documents_dir):
        print(f"Error: Documents directory '{documents_dir}' not found!")
        print(f"Please create the directory and add some .txt files to it.")
        sys.exit(1)
    
    # Check for text files
    txt_files = [f for f in os.listdir(documents_dir) if f.endswith('.txt')]
    
    if not txt_files:
        print(f"No .txt files found in '{documents_dir}' directory!")
        print("Please add some .txt files and run the script again.")
        sys.exit(1)
    
    print(f"Found {len(txt_files)} text files:")
    for file in txt_files:
        print(f"  - {file}")
    
    print("\nProcessing documents...")
    
    try:
        rag_system.add_documents(documents_dir)
        print("\n✅ RAG database updated successfully!")
        print(f"📁 Processed files from: {documents_dir}")
        print(f"⚙️  Chunk size: {rag_system.chunk_size}")
        print(f"🔄 Chunk overlap: {rag_system.chunk_overlap}")
        print(f"🔍 Top-K results: {rag_system.top_k}")
        
    except Exception as e:
        print(f"\n❌ Error updating RAG database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()