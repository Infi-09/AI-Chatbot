"""
FastAPI Backend for AI Chatbot with Memory and Personality
"""

import uvicorn # type: ignore
from typing import List, Dict, Optional
from pydantic import BaseModel # type: ignore
from fastapi import FastAPI, HTTPException  # type: ignore
from fastapi.responses import FileResponse # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore

from src.vector_memory import VectorMemoryStore
from src.personality_engine import PersonalityEngine
from src.memory_extractor import (
    MemoryExtractor, 
    ExtractedMemory, 
    UserPreference, 
    EmotionalPattern, 
    Fact
)

app = FastAPI(title="AI Chatbot with Memory & Personality")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize modules
memory_extractor = MemoryExtractor()
personality_engine = PersonalityEngine()
vector_memory_store = VectorMemoryStore()

# Request/Response models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    personality: Optional[str] = "default"
    user_name: Optional[str] = "default_user"

class MemoryExtractionRequest(BaseModel):
    messages: List[Message]
    user_name: Optional[str] = "default_user"

class ComparisonRequest(BaseModel):
    messages: List[Message]
    memory: Optional[Dict] = None
    user_name: Optional[str] = "default_user"

class ChatResponse(BaseModel):
    response: str
    memory: Optional[Dict] = None

class ComparisonResponse(BaseModel):
    comparisons: Dict[str, str]
    memory_summary: str

@app.get("/")
async def root():
    """Serve the main HTML page"""
    return FileResponse("static/index.html")

@app.get("/api/personalities")
async def get_personalities():
    """Get available personalities"""
    personalities = {}
    for key, personality in PersonalityEngine.PERSONALITIES.items():
        personalities[key] = {
            "name": personality.name,
            "description": personality.description
        }
    return {"personalities": personalities}

@app.post("/api/extract-memory")
async def extract_memory(request: MemoryExtractionRequest):
    """Extract memory from messages and store in vector database"""
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        memory = memory_extractor.extract_memory(messages)
        
        # Store in vector database
        conversation_context = " ".join([msg.get("content", "") for msg in messages[-5:]])
        vector_memory_store.store_memory(
            user_name=request.user_name,
            memory=memory,
            conversation_context=conversation_context
        )
        
        return {
            "preferences": [p.model_dump() for p in memory.preferences],
            "emotional_patterns": [e.model_dump() for e in memory.emotional_patterns],
            "facts": [f.model_dump() for f in memory.facts],
            "summary": memory_extractor.get_memory_summary(memory)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Generate chat response with personality and vector memory retrieval"""
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        user_name = request.user_name or "default_user"
        
        # Retrieve existing memories from vector database
        existing_memory = vector_memory_store.retrieve_memories(
            user_name=user_name,
            n_results=15
        )
        
        # Extract memory from recent messages (last 30)
        recent_messages = messages[-30:] if len(messages) > 30 else messages
        new_memory = memory_extractor.extract_memory(recent_messages)
        
        # Merge existing and new memories
        merged_memory = vector_memory_store.merge_memories(existing_memory, new_memory)
        
        # Store the new memory in vector database
        conversation_context = " ".join([msg.get("content", "") for msg in recent_messages[-5:]])
        vector_memory_store.store_memory(
            user_name=user_name,
            memory=new_memory,
            conversation_context=conversation_context
        )
        
        # Generate response with personality using merged memory
        response = personality_engine.generate_response(
            messages,
            request.personality,
            merged_memory
        )
        
        return ChatResponse(
            response=response,
            memory={
                "preferences": [p.model_dump() for p in merged_memory.preferences],
                "emotional_patterns": [e.model_dump() for e in merged_memory.emotional_patterns],
                "facts": [f.model_dump() for f in merged_memory.facts]
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compare-personalities")
async def compare_personalities(request: ComparisonRequest):
    """Compare responses across different personalities"""
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        user_name = request.user_name or "default_user"
        
        
        # Retrieve from vector database
        existing_memory = vector_memory_store.retrieve_memories(
            user_name=user_name,
            n_results=15
        )
        
        # Also extract from recent messages and merge
        recent_messages = messages[-30:] if len(messages) > 30 else messages
        new_memory = memory_extractor.extract_memory(recent_messages)
        memory = vector_memory_store.merge_memories(existing_memory, new_memory)
        
        # Generate comparisons
        comparisons = personality_engine.compare_responses(messages, memory)
        
        return ComparisonResponse(
            comparisons=comparisons,
            memory_summary=memory_extractor.get_memory_summary(memory)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

