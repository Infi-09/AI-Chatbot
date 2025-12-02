const API_BASE = '/api';
let messages = [];
let currentPersonality = 'default';
let currentMemory = null;
let userName = localStorage.getItem('userName') || 'default_user';

// Load saved user name on page load
window.addEventListener('DOMContentLoaded', () => {
    const userNameInput = document.getElementById('userNameInput');
    if (userNameInput && userName !== 'default_user') {
        userNameInput.value = userName;
    }
});

function saveUserName() {
    const input = document.getElementById('userNameInput');
    const name = input.value.trim();
    if (name) {
        userName = name;
        localStorage.setItem('userName', name);
        alert(`Name saved as: ${name}. Your memories will be stored and retrieved automatically!`);
    } else {
        alert('Please enter a valid name');
    }
}

// Initialize personality buttons
document.querySelectorAll('.personality-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.personality-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentPersonality = btn.dataset.personality;
    });
});

async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessageToChat('user', message);
    messages.push({ role: 'user', content: message });
    input.value = '';
    
    // Disable input
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = true;
    sendBtn.textContent = 'Thinking...';

    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                messages: messages,
                personality: currentPersonality,
                user_name: userName
            })
        });

        const data = await response.json();
        
        // Add assistant response
        addMessageToChat('assistant', data.response, currentPersonality);
        messages.push({ role: 'assistant', content: data.response });

        // Update memory display
        if (data.memory) {
            currentMemory = data.memory;
            updateMemoryDisplay(data.memory);
        }
    } catch (error) {
        addMessageToChat('assistant', `Error: ${error.message}`, 'error');
    } finally {
        sendBtn.disabled = false;
        sendBtn.textContent = 'Send';
    }
}

function addMessageToChat(role, content, label = '') {
    const container = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    if (label && role === 'assistant') {
        const labelDiv = document.createElement('div');
        labelDiv.className = 'message-label';
        labelDiv.textContent = `[${label}]`;
        messageDiv.appendChild(labelDiv);
    }
    
    const contentDiv = document.createElement('div');
    contentDiv.textContent = content;
    messageDiv.appendChild(contentDiv);
    
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function updateMemoryDisplay(memory) {
    const display = document.getElementById('memoryDisplay');
    let html = '';

    if (memory.preferences && memory.preferences.length > 0) {
        html += '<div class="memory-item"><strong>Preferences:</strong><ul>';
        memory.preferences.forEach(p => {
            html += `<li>${p.preference} (${p.category}) - Confidence: ${(p.confidence * 100).toFixed(0)}%</li>`;
        });
        html += '</ul></div>';
    }

    if (memory.emotional_patterns && memory.emotional_patterns.length > 0) {
        html += '<div class="memory-item"><strong>Emotional Patterns:</strong><ul>';
        memory.emotional_patterns.forEach(e => {
            html += `<li>${e.emotion}: ${e.context} (Frequency: ${e.frequency})</li>`;
        });
        html += '</ul></div>';
    }

    if (memory.facts && memory.facts.length > 0) {
        html += '<div class="memory-item"><strong>Facts:</strong><ul>';
        memory.facts.forEach(f => {
            html += `<li>${f.fact} (${f.category}) - Importance: ${(f.importance * 100).toFixed(0)}%</li>`;
        });
        html += '</ul></div>';
    }

    if (!html) {
        html = '<p style="color: #999; text-align: center; padding: 20px;">No memory extracted yet. Keep chatting!</p>';
    }

    display.innerHTML = html;
}

async function comparePersonalities() {
    if (messages.length === 0) {
        alert('Please start a conversation first!');
        return;
    }

    const section = document.getElementById('comparisonSection');
    const container = document.getElementById('comparisonContainer');
    
    section.style.display = 'block';
    container.innerHTML = '<div class="loading">Generating comparisons...</div>';

    try {
        const response = await fetch(`${API_BASE}/compare-personalities`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                messages: messages,
                memory: currentMemory,
                user_name: userName
            })
        });

        const data = await response.json();
        container.innerHTML = '';

        const personalityNames = {
            'default': 'Default',
            'calm_mentor': 'Calm Mentor',
            'witty_friend': 'Witty Friend',
            'therapist': 'Therapist'
        };

        for (const [key, response] of Object.entries(data.comparisons)) {
            const card = document.createElement('div');
            card.className = 'comparison-card';
            card.innerHTML = `
                <h3>${personalityNames[key]}</h3>
                <div class="comparison-text">${response}</div>
            `;
            container.appendChild(card);
        }

        // Scroll to comparison
        section.scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        container.innerHTML = `<div class="error">Error: ${error.message}</div>`;
    }
}

function clearChat() {
    if (confirm('Are you sure you want to clear the chat?')) {
        messages = [];
        currentMemory = null;
        document.getElementById('chatContainer').innerHTML = '';
        document.getElementById('memoryDisplay').innerHTML = '<p style="color: #999; text-align: center; padding: 20px;">Memory will appear here as you chat.</p>';
        document.getElementById('comparisonSection').style.display = 'none';
    }
}

// Load sample conversation on page load
window.addEventListener('load', () => {
    const welcomeMsg = userName !== 'default_user' 
        ? `Hello ${userName}! I'm an AI assistant with memory and personality. I'll remember things about you and retrieve them automatically. You can also switch between different personality styles!`
        : 'Hello! I\'m an AI assistant with memory and personality. Please enter your name above to enable automatic memory storage and retrieval. Try chatting with me, and I\'ll remember things about you. You can also switch between different personality styles!';
    addMessageToChat('assistant', welcomeMsg, 'system');
});