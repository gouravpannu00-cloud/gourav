// English Tutor - AI Tutor Chat JavaScript

function setupChat() {
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendMessageBtn');
    const exampleBtns = document.querySelectorAll('.example-btn');

    if (sendBtn) {
        sendBtn.addEventListener('click', sendMessage);
    }

    if (chatInput) {
        chatInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    // Example prompt buttons
    exampleBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const text = this.textContent.replace(/"/g, '');
            if (chatInput) {
                chatInput.value = text;
                sendMessage();
            }
        });
    });
}

async function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');

    if (!chatInput || !chatMessages) return;

    const message = chatInput.value.trim();
    if (!message) return;

    // Add user message
    addMessage(message, 'user');
    chatInput.value = '';

    // Show typing indicator
    const typingId = addTypingIndicator();

    try {
        const data = await apiRequest('/tutor/chat', {
            method: 'POST',
            body: JSON.stringify({ message: message })
        });

        // Remove typing indicator
        removeTypingIndicator(typingId);

        // Add tutor response with correction details
        addTutorResponse(data);
    } catch (error) {
        removeTypingIndicator(typingId);
        addMessage('Sorry, I encountered an error. Please try again.', 'tutor');
        console.error('Chat error:', error);
    }
}

function addMessage(content, type) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;

    const avatar = type === 'user' ? '👤' : '🤖';

    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <p>${content}</p>
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addTutorResponse(data) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message tutor-message';

    const avatar = '🤖';

    // Build correction display
    let correctionsHtml = '';
    if (data.analysis && data.analysis.corrections && data.analysis.corrections.length > 0) {
        correctionsHtml = `
            <div class="corrections-section">
                <h4>Corrections:</h4>
                ${data.analysis.corrections.map(c => `
                    <div class="correction-item">
                        <span class="correction-type">${c.type}</span>
                        <span class="correction-original">${c.original}</span>
                        <span class="correction-arrow">→</span>
                        <span class="correction-fixed">${c.corrected}</span>
                        <p class="correction-explanation">${c.explanation}</p>
                    </div>
                `).join('')}
            </div>
        `;
    }

    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <p>${data.response}</p>
            ${data.analysis && data.analysis.has_errors ? `
                <div class="analysis-section">
                    <div class="analysis-card">
                        <div class="analysis-row">
                            <strong>Original:</strong>
                            <span>${data.analysis.original}</span>
                        </div>
                        <div class="analysis-row">
                            <strong>Corrected:</strong>
                            <span class="corrected-text">${data.analysis.corrected}</span>
                        </div>
                    </div>
                </div>
            ` : ''}
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return null;

    const id = 'typing-' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.id = id;
    messageDiv.className = 'message tutor-message';

    messageDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <p class="typing-indicator">Typing...</p>
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return id;
}

function removeTypingIndicator(id) {
    if (!id) return;
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}
