"""
Vector Memory Storage Module

This module handles storing and retrieving user memories in a vector database.
Memories are stored with user_name for automatic retrieval.
"""

import time
import json
import chromadb # type: ignore
from chromadb.config import Settings # type: ignore

from src.memory_extractor import (
    ExtractedMemory,
    UserPreference,
    EmotionalPattern,
    Fact
)


class VectorMemoryStore:
    """Manages vector database storage and retrieval of user memories"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the vector memory store.
        
        Args:
            persist_directory: Directory to persist the ChromaDB database
        """
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection for memories
        self.collection = self.client.get_or_create_collection(
            name="user_memories",
            metadata={"hnsw:space": "cosine"}
        )
    
    def store_memory(
        self,
        user_name: str,
        memory: ExtractedMemory,
        conversation_context: str = ""
    ) -> None:
        """
        Store extracted memory in the vector database.
        
        Args:
            user_name: Name of the user
            memory: ExtractedMemory object to store
            conversation_context: Optional context from the conversation
        """
        # Create documents from memory components
        documents = []
        metadatas = []
        ids = []
        
        timestamp = int(time.time() * 1000000)  # Microsecond timestamp for uniqueness
        
        # Store preferences
        for idx, pref in enumerate(memory.preferences):
            doc_text = f"User preference: {pref.preference} in category {pref.category}. Confidence: {pref.confidence}"
            if conversation_context:
                doc_text += f" Context: {conversation_context}"
            
            documents.append(doc_text)
            metadatas.append({
                "user_name": user_name,
                "type": "preference",
                "category": pref.category,
                "confidence": str(pref.confidence),
                "data": json.dumps(pref.model_dump())
            })
            ids.append(f"{user_name}_pref_{timestamp}_{idx}")
        
        # Store emotional patterns
        for idx, pattern in enumerate(memory.emotional_patterns):
            doc_text = f"Emotional pattern: {pattern.emotion} in context {pattern.context}. Frequency: {pattern.frequency}"
            if pattern.triggers:
                doc_text += f" Triggers: {', '.join(pattern.triggers)}"
            if conversation_context:
                doc_text += f" Context: {conversation_context}"
            
            documents.append(doc_text)
            metadatas.append({
                "user_name": user_name,
                "type": "emotional_pattern",
                "emotion": pattern.emotion,
                "frequency": str(pattern.frequency),
                "data": json.dumps(pattern.model_dump())
            })
            ids.append(f"{user_name}_emotion_{timestamp}_{idx}")
        
        # Store facts
        for idx, fact in enumerate(memory.facts):
            doc_text = f"Fact about user: {fact.fact} in category {fact.category}. Importance: {fact.importance}"
            if fact.context:
                doc_text += f" Context: {fact.context}"
            if conversation_context:
                doc_text += f" Additional context: {conversation_context}"
            
            documents.append(doc_text)
            metadatas.append({
                "user_name": user_name,
                "type": "fact",
                "category": fact.category,
                "importance": str(fact.importance),
                "data": json.dumps(fact.model_dump())
            })
            ids.append(f"{user_name}_fact_{timestamp}_{idx}")
        
        # Add to collection if we have documents
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
    
    def retrieve_memories(
        self,
        user_name: str,
        n_results: int = 10
    ) -> ExtractedMemory:
        """
        Retrieve relevant memories for a user.
        
        Args:
            user_name: Name of the user
            query: Optional query text for semantic search (if None, returns all user memories)
            n_results: Number of results to return
            
        Returns:
            ExtractedMemory object with retrieved memories
        """
        # Filter by user_name
        where_filter = {"user_name": user_name}
        
        # Get all memories for user
        results = self.collection.get(
            where=where_filter,
            limit=n_results
        )
        
        # Reconstruct ExtractedMemory from results
        preferences = []
        emotional_patterns = []
        facts = []
        
        if results and results.get('metadatas'):
            for metadata, doc in zip(results['metadatas'], results.get('documents', [])):
                if not metadata:
                    continue
                    
                data_str = metadata.get('data', '{}')
                try:
                    data = json.loads(data_str)
                    mem_type = metadata.get('type', '')
                    
                    if mem_type == 'preference':
                        preferences.append(UserPreference(**data))
                    elif mem_type == 'emotional_pattern':
                        emotional_patterns.append(EmotionalPattern(**data))
                    elif mem_type == 'fact':
                        facts.append(Fact(**data))
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Error parsing memory data: {e}")
                    continue
        
        return ExtractedMemory(
            preferences=preferences,
            emotional_patterns=emotional_patterns,
            facts=facts
        )
    
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
        # Get all IDs for this user
        results = self.collection.get(where={"user_name": user_name})
        if results and results.get('ids'):
            self.collection.delete(ids=results['ids'])

