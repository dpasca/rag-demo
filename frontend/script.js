class ChatApp {
    constructor() {
        this.chatMessages = document.getElementById('chat-messages');
        this.userInput = document.getElementById('user-input');
        this.sendButton = document.getElementById('send-button');
        this.status = document.getElementById('status');
        this.conversationHistory = [];

        this.init();
    }

    init() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
    }

    async sendMessage() {
        const message = this.userInput.value.trim();
        if (!message) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        this.userInput.value = '';
        this.setStatus('Thinking...');

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    conversation_history: this.conversationHistory
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Add assistant message to chat
            this.addMessage(data.message, 'assistant', data.rag_used, data.rag_sources);
            
            // Update conversation history
            this.conversationHistory.push({ role: 'user', content: message });
            this.conversationHistory.push({ role: 'assistant', content: data.message });

            this.setStatus('');

        } catch (error) {
            console.error('Error:', error);
            this.addMessage('Sorry, there was an error processing your request.', 'assistant');
            this.setStatus('Error occurred');
        }
    }

    addMessage(content, role, ragUsed = false, ragSources = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;

        // Convert newlines to <br> tags for proper formatting
        const formattedContent = content.replace(/\n/g, '<br>');
        
        let messageHTML = `
            <div class="message-content">
                <strong>${role === 'user' ? 'You' : 'Assistant'}:</strong> ${formattedContent}
            </div>
        `;

        // Add RAG sources if available
        if (ragUsed && ragSources && ragSources.length > 0) {
            messageHTML += '<div class="rag-sources">';
            messageHTML += '<div class="rag-header">📚 Sources:</div>';
            ragSources.forEach((source, index) => {
                messageHTML += `
                    <div class="rag-source">
                        <div class="source-info">
                            <span class="source-file">${source.filename}</span>
                            <span class="source-chunk">chunk ${source.chunk_index}</span>
                        </div>
                        <div class="source-content">${this.truncateText(source.content, 200)}</div>
                    </div>
                `;
            });
            messageHTML += '</div>';
        }

        messageDiv.innerHTML = messageHTML;
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    setStatus(message) {
        this.status.textContent = message;
    }
}

// Initialize the chat app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});