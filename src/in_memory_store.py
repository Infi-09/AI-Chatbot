"""
In-Memory Memory Store for Serverless Environments

This module provides an in-memory alternative to VectorMemoryStore
for serverless deployments where persistent storage isn't available.
"""

from src.memory_extractor import ExtractedMemory


class InMemoryStore:
    """In-memory storage for user memories (serverless-friendly)"""
    
    def __init__(self):
        """Initialize in-memory storage"""
        self._memories: dict[str, ExtractedMemory] = {}
    
    def store_memory(
        self,
        user_name: str,
        memory: ExtractedMemory,
    ) -> None:
        """
        Store extracted memory in memory (merged with existing).
        
        Args:
            user_name: Name of the user
            memory: ExtractedMemory object to store
        """
        # Get existing memory or create empty one
        existing = self._memories.get(user_name, ExtractedMemory(
            preferences=[],
            emotional_patterns=[],
            facts=[]
        ))
        
        # Merge with existing memory
        merged = self.merge_memories(existing, memory)
        
        # Store merged memory
        self._memories[user_name] = merged
    
    def retrieve_memories(
        self,
        user_name: str,
    ) -> ExtractedMemory:
        """
        Retrieve memories for a user.
        
        Args:
            user_name: Name of the user
            n_results: Number of results to return (not used in-memory, returns all)
            
        Returns:
            ExtractedMemory object with retrieved memories
        """
        # Return existing memory or empty one
        return self._memories.get(user_name, ExtractedMemory(
            preferences=[],
            emotional_patterns=[],
            facts=[]
        ))
    
    def merge_memories(
        self,
        existing: ExtractedMemory,
        new: ExtractedMemory
    ) -> ExtractedMemory:
        """
        Merge new memories with existing ones, avoiding duplicates.
        
        Args:
            existing: Existing ExtractedMemory
            new: New ExtractedMemory to merge
            
        Returns:
            Merged ExtractedMemory
        """
        # Merge preferences (avoid duplicates based on category and preference)
        existing_prefs = {(p.category, p.preference.lower()) for p in existing.preferences}
        merged_prefs = existing.preferences.copy()
        for pref in new.preferences:
            key = (pref.category, pref.preference.lower())
            if key not in existing_prefs:
                merged_prefs.append(pref)
            else:
                # Update confidence if new one is higher
                for i, ep in enumerate(merged_prefs):
                    if (ep.category, ep.preference.lower()) == key:
                        if pref.confidence > ep.confidence:
                            merged_prefs[i] = pref
                        break
        
        # Merge emotional patterns (avoid duplicates based on emotion and context)
        existing_emotions = {(e.emotion.lower(), e.context.lower()) for e in existing.emotional_patterns}
        merged_emotions = existing.emotional_patterns.copy()
        for emotion in new.emotional_patterns:
            key = (emotion.emotion.lower(), emotion.context.lower())
            if key not in existing_emotions:
                merged_emotions.append(emotion)
            else:
                # Update frequency
                for i, ee in enumerate(merged_emotions):
                    if (ee.emotion.lower(), ee.context.lower()) == key:
                        merged_emotions[i].frequency += emotion.frequency
                        break
        
        # Merge facts (avoid duplicates based on fact text)
        existing_facts = {f.fact.lower() for f in existing.facts}
        merged_facts = existing.facts.copy()
        for fact in new.facts:
            if fact.fact.lower() not in existing_facts:
                merged_facts.append(fact)
            else:
                # Update importance if new one is higher
                for i, ef in enumerate(merged_facts):
                    if ef.fact.lower() == fact.fact.lower():
                        if fact.importance > ef.importance:
                            merged_facts[i] = fact
                        break
        
        return ExtractedMemory(
            preferences=merged_prefs,
            emotional_patterns=merged_emotions,
            facts=merged_facts
        )
    
    def delete_user_memories(self, user_name: str) -> None:
        """
        Delete all memories for a specific user.
        
        Args:
            user_name: Name of the user
        """
        if user_name in self._memories:
            del self._memories[user_name]

