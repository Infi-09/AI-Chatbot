"""
Memory Extraction Module

This module extracts and structures user information from chat messages:
- User preferences
- Emotional patterns
- Facts worth remembering
"""

import re
import json
from typing import List, Dict
from pydantic import BaseModel # type: ignore

from src.models import load_model


class UserPreference(BaseModel):
    """Represents a user preference"""
    category: str
    preference: str
    confidence: float  # 0.0 to 1.0

class EmotionalPattern(BaseModel):
    """Represents an emotional pattern"""
    emotion: str
    context: str
    frequency: int
    triggers: List[str]

class Fact(BaseModel):
    """Represents a fact worth remembering"""
    fact: str
    category: str
    importance: float  # 0.0 to 1.0
    context: str

class ExtractedMemory(BaseModel):
    """Complete memory extraction result"""
    preferences: List[UserPreference]
    emotional_patterns: List[EmotionalPattern]
    facts: List[Fact]

class MemoryExtractor:
    """Extracts structured memory from chat messages"""
    
    def __init__(self, api_key: str = None):
        self.client = load_model()
        self.model = "gemini-2.5-flash"
    
    def extract_memory(self, messages: List[Dict[str, str]]) -> ExtractedMemory:
        """
        Extract memory from a list of chat messages.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            
        Returns:
            ExtractedMemory object with preferences, emotional patterns, and facts
        """
        
        # Prepare the conversation context
        conversation_text = self._format_conversation(messages)
        
        # Create extraction prompt
        extraction_prompt = f"""Analyze the following conversation and extract structured information about the user.

Conversation:
{conversation_text}

Extract the following information:

1. USER PREFERENCES:
   - Identify any preferences the user has expressed (likes, dislikes, interests, hobbies, etc.)
   - Include category (e.g., "food", "music", "work", "hobbies") and the specific preference
   - Rate confidence from 0.0 to 1.0

2. EMOTIONAL PATTERNS:
   - Identify emotional states expressed by the user (happy, stressed, anxious, excited, etc.)
   - Note the context in which these emotions appear
   - Identify potential triggers or patterns
   - Count frequency if emotions repeat

3. FACTS WORTH REMEMBERING:
   - Extract important facts about the user (name, location, job, relationships, goals, etc.)
   - Include context where the fact was mentioned
   - Rate importance from 0.0 to 1.0

Return the result as a JSON object with this exact structure:
{{
    "preferences": [
        {{"category": "string", "preference": "string", "confidence": 0.0-1.0}}
    ],
    "emotional_patterns": [
        {{"emotion": "string", "context": "string", "frequency": int, "triggers": ["string"]}}
    ],
    "facts": [
        {{"fact": "string", "category": "string", "importance": 0.0-1.0, "context": "string"}}
    ]
}}

Be thorough and extract all relevant information. If a category is empty, return an empty array."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=f"You are an expert at analyzing conversations and extracting structured information about users. Always return valid JSON. {extraction_prompt}" 
            )
            
            result = self.extract_json_from_llm(response.text)
            
            # Parse into Pydantic models
            return ExtractedMemory(
                preferences=[UserPreference(**p) for p in result.get("preferences", [])],
                emotional_patterns=[EmotionalPattern(**e) for e in result.get("emotional_patterns", [])],
                facts=[Fact(**f) for f in result.get("facts", [])]
            )
            
        except Exception as e:
            print(f"Error in memory extraction: {e}")
            # Return empty memory on error
            return ExtractedMemory(
                preferences=[],
                emotional_patterns=[],
                facts=[]
            )
    
    def _format_conversation(self, messages: List[Dict[str, str]]) -> str:
        """Format messages into a readable conversation string"""
        formatted = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            formatted.append(f"{role.upper()}: {content}")
        return "\n".join(formatted)
    
    def get_memory_summary(self, memory: ExtractedMemory) -> str:
        """Generate a human-readable summary of extracted memory"""
        summary_parts = []
        
        if memory.preferences:
            summary_parts.append("PREFERENCES:")
            for pref in memory.preferences:
                summary_parts.append(f"  - {pref.category}: {pref.preference} (confidence: {pref.confidence:.2f})")
        
        if memory.emotional_patterns:
            summary_parts.append("\nEMOTIONAL PATTERNS:")
            for pattern in memory.emotional_patterns:
                summary_parts.append(f"  - {pattern.emotion}: {pattern.context} (frequency: {pattern.frequency})")
                if pattern.triggers:
                    summary_parts.append(f"    Triggers: {', '.join(pattern.triggers)}")
        
        if memory.facts:
            summary_parts.append("\nFACTS:")
            for fact in memory.facts:
                summary_parts.append(f"  - {fact.fact} ({fact.category}, importance: {fact.importance:.2f})")
        
        return "\n".join(summary_parts) if summary_parts else "No memory extracted yet."

    def extract_json_from_llm(self, text: str) -> dict | None:
        """
        Extracts and returns JSON data from an LLM response.
        The LLM should return JSON inside ```json ... ``` blocks.
        """
        try:
            # Find the content inside ```json ... ```
            match = re.search(r"```json(.*?)```", text, flags=re.S)
            if not match:
                return None
            
            json_str = match.group(1).strip()

            # Parse JSON
            return json.loads(json_str)
        
        except Exception as e:
            print("JSON parse error:", e)
            return {}
