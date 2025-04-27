async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value;
    if (!message) return;

    // Display user message
    appendMessage('YOU: ' + message, 'user-message');
    input.value = '';

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        const data = await response.json();
        if (data.error) {
            appendMessage('ERROR: ' + data.error, 'error-message');
        } else if (data.response) {
            appendMessage('ASSISTANT: ' + data.response, 'bot-message');
        } else {
            appendMessage('Error: Invalid response format', 'error-message');
        }
    } catch (error) {
        appendMessage('Error: Failed to get response', 'error-message');
    }
}
async function K_event() {
    let i = document.getElementById('chatInput')
    i.addEventListener('keydown', (e) => {
        if (e.key == 'Enter') {
            sendMessage();
        }
    })
}
K_event()
document.addEventListener("DOMContentLoaded", function () {
    const cbIcon = document.querySelector('.cb-icon');
    const chatContainer = document.querySelector('.chat-container');

    // Toggle visibility on icon click
    cbIcon.addEventListener('click', function (e) {
        e.stopPropagation(); // Stop the click from bubbling to document
        const isVisible = chatContainer.style.display === 'flex';
        chatContainer.style.display = isVisible ? 'none' : 'flex';
    });

    // Prevent hiding when clicking inside the chat container
    chatContainer.addEventListener('click', function (e) {
        e.stopPropagation();
    });

    // Hide when clicking outside
    document.addEventListener('click', function () {
        chatContainer.style.display = 'none';
    });
});
function appendMessage(message, className) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageElement = document.createElement('div');
    messageElement.className = 'chat-message ' + className;
    messageElement.textContent = message;
    messagesDiv.appendChild(messageElement);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}