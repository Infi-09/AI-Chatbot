# AI Chatbot with Memory & Personality Engine

A sophisticated AI chatbot system that extracts user memory and adapts its personality based on conversation context.

## Features

### 🧠 Memory Extraction Module
- **User Preferences**: Identifies likes, dislikes, interests, and hobbies
- **Emotional Patterns**: Tracks emotional states, contexts, and triggers
- **Facts**: Remembers important information about the user (name, location, job, goals, etc.)

### 🎭 Personality Engine
- **Calm Mentor**: Thoughtful, wise, and patient guidance
- **Witty Friend**: Light-hearted, humorous, and engaging
- **Therapist**: Professional, empathetic, and supportive
- **Default**: Standard helpful assistant

### 🔄 Before/After Comparison
- Compare how the same conversation would look with different personalities
- See how memory influences responses across personality styles

## Architecture

```
|-- static/
|   |--  index.html        # Frontend interface
|   |--  script.js         # JS Script
|   |--  styles.css        # Frontend CSS
|-- src/
|   |--  in_memory_store.py     # Store User Preferences in InMemory (For deploying in Vercel)
|   |--  memory_extractor.py    # Memory extraction module
|   |--  models.py              # Load Gemini Model
|   |--  personality_engine.py  # Personality transformation engine
|   |--  vector_memory.py       # Store User Preferences in Vector DB (ChromaDB)
|-- demo.py                # Run this file for quick demo
|-- main.py                # FastAPI backend
|-- main_vercel.py         # FastAPI backend (Vercel version)
|-- requirements.txt       # Python dependencies
```

## Setup

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/Infi-09/AI-Chatbot.git
   cd AI-Chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

4. **Run the application**
   ```bash
   python main.py
   # Or with uvicorn directly:
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the application**
   - Open http://localhost:8000 in your browser

### Running the Demo

To quickly test the memory extraction and personality features without starting the full web server:

```bash
python demo.py
```

**Note**: Make sure you have set your `GEMINI_API_KEY` environment variable before running the demo.

The demo will:
- Process 30 sample conversation messages
- Extract and display user memory (preferences, emotional patterns, facts)
- Generate responses from all personality types (Default, Calm Mentor, Witty Friend, Therapist)
- Show how different personalities respond to the same input

## ⚠️ Important Notes

### Memory Storage Options

**`main.py` vs `main_vercel.py`:**

- **`main.py`**: Uses **ChromaDB** (vector database) for persistent memory storage
  - Memory is stored in `./chroma_db/` directory
  - Uses `src/vector_memory.py` (`VectorMemoryStore` class)
  - **Best for**: Local development and deployments with persistent storage

- **`main_vercel.py`**: Uses **in-memory storage** (no persistence)
  - Memory is stored temporarily in RAM during the session
  - Uses `src/in_memory_store.py` (`InMemoryStore` class)
  - **Best for**: Serverless deployments (Vercel, AWS Lambda, etc.)


**Key Differences:**
- `main.py` → ChromaDB → Persistent storage → Better for production with file system access
- `main_vercel.py` → InMemoryStore → Temporary storage → Required for serverless platforms


## API Endpoints

### `GET /`
Serves the main HTML interface

### `GET /api/personalities`
Returns available personality options

### `POST /api/extract-memory`
Extracts memory from conversation messages
```json
{
  "messages": [
    {"role": "user", "content": "I love pizza"},
    {"role": "assistant", "content": "That's great!"}
  ]
}
```

### `POST /api/chat`
Generates a chat response with selected personality
```json
{
  "messages": [...],
  "personality": "calm_mentor"
}
```

### `POST /api/compare-personalities`
Compares responses across all personalities
```json
{
  "messages": [...],
  "memory": {...}
}
```

## Example Conversation

**User**: "I'm feeling stressed about my upcoming exam. I love studying with music, especially jazz."

**Memory Extracted**:
- Preference: Music (jazz) - Confidence: 0.9
- Emotional Pattern: Stressed (exam context) - Frequency: 1
- Fact: Has upcoming exam - Importance: 0.8

**Calm Mentor Response**: "I understand that exams can be stressful. It's wonderful that you've found jazz music to be a helpful study companion. Have you considered creating a structured study plan? Sometimes breaking down the material into manageable chunks can help reduce that stress..."

**Witty Friend Response**: "Ah, the classic exam stress! At least you've got good taste in study music - jazz is smooth like your brain will be after acing that test! 🎷 Want to talk about study strategies, or just vent about the stress?"

**Therapist Response**: "I hear that you're experiencing stress around your exam. That's completely understandable. Music, especially jazz, seems to be a helpful coping mechanism for you. Can you tell me more about what specifically is causing the stress? Is it the amount of material, the time pressure, or something else?"


