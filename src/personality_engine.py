"""
Personality Engine

This module transforms the agent's reply tone based on selected personality:
- Calm Mentor
- Witty Friend
- Therapist-style
"""

from typing import List, Dict, Optional
from src.memory_extractor import ExtractedMemory

from src.models import load_model


class Personality:
    """Personality configuration"""
    def __init__(self, name: str, system_prompt: str, description: str):
        self.name = name
        self.system_prompt = system_prompt
        self.description = description

class PersonalityEngine:
    """Manages different personality styles for the chatbot"""
    
    PERSONALITIES = {
        "calm_mentor": Personality(
            name="Calm Mentor",
            system_prompt="""You are a calm, wise, and patient mentor. Your communication style is:
- Thoughtful and reflective
- Encouraging but realistic
- Uses analogies and gentle guidance
- Maintains a calm, steady tone even when discussing difficult topics
- Asks probing questions to help the user think deeper
- Provides balanced perspectives
- Never judgmental, always supportive
- Keep the conversation concise and only respond with more words if necessary""",
            description="A wise, patient guide who offers thoughtful advice"
        ),
        "witty_friend": Personality(
            name="Witty Friend",
            system_prompt="""You are a witty, humorous, and engaging friend. Your communication style is:
- Light-hearted and fun
- Uses humor and wit appropriately
- Casual and conversational
- Makes jokes and references that feel natural
- Energetic and enthusiastic
- Relatable and down-to-earth
- Still supportive, but with a playful edge
- Keep the conversation concise and only respond with more words if necessary""",
            description="A fun, humorous companion who keeps things light"
        ),
        "therapist": Personality(
            name="Therapist",
            system_prompt="""You are a professional, empathetic therapist. Your communication style is:
- Warm and non-judgmental
- Uses active listening techniques
- Asks open-ended questions
- Validates emotions
- Helps users explore their feelings
- Maintains professional boundaries
- Focuses on emotional well-being and self-discovery
- Uses therapeutic techniques like reflection and reframing
- Keep the conversation concise and only respond with more words if necessary""",
            description="A professional, empathetic guide for emotional support"
        ),
        "default": Personality(
            name="Default",
            system_prompt="You are a helpful, friendly AI assistant.",
            description="Standard helpful assistant"
        )
    }
    
    def __init__(self):
        self.client = load_model()
        self.model = "gemini-2.5-flash"
        self.current_personality = "default"
    
    def set_personality(self, personality_key: str):
        """Set the active personality"""
        if personality_key in self.PERSONALITIES:
            self.current_personality = personality_key
        else:
            self.current_personality = "default"
    
    def get_personality(self, personality_key: str = None) -> Personality:
        """Get personality by key"""
        key = personality_key or self.current_personality
        return self.PERSONALITIES.get(key, self.PERSONALITIES["default"])
    
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        personality_key: str = None,
        memory: Optional[ExtractedMemory] = None
    ) -> str:
        """
        Generate a response with the specified personality.
        
        Args:
            messages: Conversation history
            personality_key: Which personality to use
            memory: Extracted memory to inform the response
            
        Returns:
            Generated response string
        """
        personality = self.get_personality(personality_key)
        
        # Build system prompt with personality and memory context
        system_prompt = personality.system_prompt
        system_prompt += f"\n\nUser's last message: {messages[-1]['content']}"

        if memory:
            memory_context = self._build_memory_context(memory)
            system_prompt += f"\n\nIMPORTANT CONTEXT ABOUT THE USER:\n{memory_context}\n\nUse this information to personalize your responses while maintaining your personality style."
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=system_prompt,
            )
            
            return response.text
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def _build_memory_context(self, memory: ExtractedMemory) -> str:
        """Build a context string from extracted memory"""
        context_parts = []
        
        if memory.preferences:
            prefs = ", ".join([f"{p.preference} ({p.category})" for p in memory.preferences[:5]])
            context_parts.append(f"Preferences: {prefs}")
        
        if memory.emotional_patterns:
            emotions = ", ".join([f"{p.emotion}" for p in memory.emotional_patterns[:3]])
            context_parts.append(f"Emotional patterns: {emotions}")
        
        if memory.facts:
            important_facts = [f for f in memory.facts if f.importance > 0.5]
            facts = "; ".join([f.fact for f in important_facts[:5]])
            if facts:
                context_parts.append(f"Important facts: {facts}")
        
        return "\n".join(context_parts) if context_parts else "No specific context available yet."
    
    def compare_responses(
        self,
        messages: List[Dict[str, str]],
        memory: Optional[ExtractedMemory] = None
    ) -> Dict[str, str]:
        """
        Generate responses with different personalities for comparison.
        
        Returns:
            Dictionary mapping personality keys to responses
        """
        comparisons = {}
        
        for key in ["default", "calm_mentor", "witty_friend", "therapist"]:
            comparisons[key] = self.generate_response(messages, key, memory)
        
        return comparisons

