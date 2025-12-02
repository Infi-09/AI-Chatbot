"""
Demo script to showcase memory extraction and personality differences
"""

import os
from src.memory_extractor import MemoryExtractor
from src.personality_engine import PersonalityEngine

def demo():
    """Demonstrate memory extraction and personality differences"""
    
    # Sample conversation (30 messages)
    sample_messages = [
        {"role": "user", "content": "Hi, I'm Sarah. I'm a software engineer from San Francisco."},
        {"role": "assistant", "content": "Nice to meet you, Sarah! How can I help you today?"},
        {"role": "user", "content": "I've been feeling really stressed lately. Work has been overwhelming."},
        {"role": "assistant", "content": "I'm sorry to hear that. Stress can be really tough to deal with."},
        {"role": "user", "content": "Yeah, I love my job but the deadlines are killing me. I work best when I listen to jazz music."},
        {"role": "assistant", "content": "That's interesting! Music can be a great stress reliever."},
        {"role": "user", "content": "I'm also training for a marathon. Running helps me clear my mind."},
        {"role": "assistant", "content": "That's awesome! Running is great for both physical and mental health."},
        {"role": "user", "content": "I have a dog named Max. He's a golden retriever and I love taking him to the park."},
        {"role": "assistant", "content": "Dogs are wonderful companions! Max sounds lovely."},
        {"role": "user", "content": "I'm really anxious about my upcoming presentation next week. It's for a big client."},
        {"role": "assistant", "content": "Presentations can be nerve-wracking. Have you prepared well?"},
        {"role": "user", "content": "I've prepared, but I always get nervous speaking in front of people. Public speaking is my biggest fear."},
        {"role": "assistant", "content": "That's completely understandable. Many people feel that way."},
        {"role": "user", "content": "I prefer working from home. The office environment is too distracting for me."},
        {"role": "assistant", "content": "Remote work has its benefits, especially for focus."},
        {"role": "user", "content": "I'm a vegetarian. I've been one for 5 years now."},
        {"role": "assistant", "content": "That's a significant lifestyle choice. What inspired you?"},
        {"role": "user", "content": "I love reading science fiction novels. Isaac Asimov is my favorite author."},
        {"role": "assistant", "content": "Asimov is a classic! Have you read the Foundation series?"},
        {"role": "user", "content": "Yes! I've read all of them. I also enjoy playing chess in my free time."},
        {"role": "assistant", "content": "Chess is a great mental exercise!"},
        {"role": "user", "content": "I'm planning a trip to Japan next month. It's my first time traveling to Asia."},
        {"role": "assistant", "content": "Japan is amazing! Are you excited?"},
        {"role": "user", "content": "Very excited but also a bit nervous. I don't speak Japanese."},
        {"role": "assistant", "content": "That's normal. Many people travel there without speaking the language."},
        {"role": "user", "content": "I get really happy when I see my friends. Social connections are important to me."},
        {"role": "assistant", "content": "That's wonderful! Strong relationships are key to well-being."},
        {"role": "user", "content": "I've been learning Spanish for 6 months. I practice every day for 30 minutes."},
        {"role": "assistant", "content": "Consistency is key to language learning!"},
    ]
    
    print("=" * 80)
    print("MEMORY EXTRACTION DEMO")
    print("=" * 80)
    print("\nAnalyzing 30 sample messages...\n")
    
    # Initialize modules
    extractor = MemoryExtractor()
    engine = PersonalityEngine()
    
    # Extract memory
    print("Extracting memory...")
    memory = extractor.extract_memory(sample_messages)
    
    print("\n" + "=" * 80)
    print("EXTRACTED MEMORY")
    print("=" * 80)
    print(extractor.get_memory_summary(memory))
    
    # Get last user message
    last_message = sample_messages[-1]
    test_messages = sample_messages + [
        {"role": "user", "content": "I'm feeling overwhelmed with everything I have to do. Any advice?"}
    ]
    
    print("\n" + "=" * 80)
    print("PERSONALITY COMPARISON")
    print("=" * 80)
    print(f"\nUser Message: \"{test_messages[-1]['content']}\"\n")
    
    # Generate responses with different personalities
    personalities = ["default", "calm_mentor", "witty_friend", "therapist"]
    personality_names = {
        "default": "Default Assistant",
        "calm_mentor": "Calm Mentor",
        "witty_friend": "Witty Friend",
        "therapist": "Therapist"
    }
    
    for personality in personalities:
        print(f"\n{'-' * 80}")
        print(f"{personality_names[personality].upper()}")
        print(f"{'-' * 80}")
        response = engine.generate_response(test_messages, personality, memory)
        print(response)
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    if not os.getenv("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY not set in environment variables!")
        print("Please set it in your .env file or export it.")
        exit(1)
    
    demo()

