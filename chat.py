import os
import json
from openai import OpenAI
from typing import List
from models import ChatMessage, ChatRequest, ChatResponse, RAGChunk
from rag import rag_system
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def search_documents(query: str) -> str:
    """Tool function for RAG search that can be called by the AI."""
    chunks = rag_system.query(query)
    
    if not chunks:
        return "No relevant documents found."
    
    result = f"Found {len(chunks)} relevant document chunks:\n\n"
    for i, chunk in enumerate(chunks, 1):
        result += f"**Source {i} ({chunk.filename}, chunk {chunk.chunk_index}):**\n{chunk.content}\n\n"
    
    return result

# Tool definition for OpenAI function calling
RAG_TOOL = {
    "type": "function",
    "function": {
        "name": "search_documents",
        "description": "Search through the document knowledge base to find relevant information",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to find relevant documents"
                }
            },
            "required": ["query"]
        }
    }
}

def chat_with_ai(request: ChatRequest) -> ChatResponse:
    """Handle chat request with RAG integration via tool calling."""
    
    # Prepare messages for OpenAI
    messages = []
    
    # Add system message
    messages.append({
        "role": "system",
        "content": "You are a helpful assistant with access to a document knowledge base. Use the search_documents tool when you need to find information from the documents to answer user questions."
    })
    
    # Add conversation history
    for msg in request.conversation_history:
        messages.append({"role": msg.role, "content": msg.content})
    
    # Add current user message
    messages.append({"role": "user", "content": request.message})
    
    # Call OpenAI with tool capability
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        tools=[RAG_TOOL],
        tool_choice="auto"
    )
    
    message = response.choices[0].message
    rag_used = False
    rag_sources = None
    
    # Handle tool calls
    if message.tool_calls:
        for tool_call in message.tool_calls:
            if tool_call.function.name == "search_documents":
                rag_used = True
                function_args = json.loads(tool_call.function.arguments)
                query = function_args["query"]
                
                # Get RAG results
                chunks = rag_system.query(query)
                rag_sources = chunks
                
                # Call the function
                function_result = search_documents(query)
                
                # Add function result to messages and get final response
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call.model_dump()]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": function_result
                })
                
                # Get final response
                final_response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=messages
                )
                
                return ChatResponse(
                    message=final_response.choices[0].message.content,
                    rag_used=rag_used,
                    rag_sources=rag_sources
                )
    
    return ChatResponse(
        message=message.content,
        rag_used=rag_used,
        rag_sources=rag_sources
    )