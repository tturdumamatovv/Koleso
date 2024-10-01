document.addEventListener('DOMContentLoaded', function() {
    const chatApp = document.getElementById('chat-app');
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('chat-message-input');
    const messageSubmit = document.getElementById('chat-message-submit');
    const autoScrollCheckbox = document.getElementById('auto-scroll-checkbox');
    let ws = null;

    function closeWebSocket() {
        if (ws) {
            ws.close();
            console.log('Closing existing WebSocket connection.');
        }
    }

    function openChat(roomId, userId, userName) {
        closeWebSocket();  // Close any existing WebSocket connection

        const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const wsUrl = `${protocol}${window.location.host}/ws/chat/${roomId}/`;
        ws = new WebSocket(wsUrl);

        ws.onopen = () => console.log(`WebSocket connection established to room ${roomId}`);
        ws.onerror = error => console.error('WebSocket error:', error);
        ws.onmessage = event => displayMessage(JSON.parse(event.data));
        ws.onclose = () => console.log('WebSocket connection closed');

        chatMessages.innerHTML = '';  // Clear previous messages
        document.getElementById('chat-room-title').textContent = `Административный Чат ${roomId}`;
        chatApp.style.display = 'block';
    }

    function displayMessage(data) {
        const messageElement = document.createElement('li');
        messageElement.classList.add('list-group-item', data.sender_id === document.body.getAttribute('data-user-id') ? 'user-message' : '');
        messageElement.innerHTML = `<strong>${data.sender_username}:</strong> ${data.message}`;
        chatMessages.appendChild(messageElement);
        scrollToBottom();
    }

    function scrollToBottom() {
        if (autoScrollCheckbox.checked) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    document.querySelectorAll('.chat-link').forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const roomId = this.getAttribute('data-room-id');
            const userId = this.getAttribute('data-user-id');
            const userName = this.getAttribute('data-user-username');
            openChat(roomId, userId, userName);
        });
    });


    messageSubmit.addEventListener('click', function(event) {
        event.preventDefault();
        const message = messageInput.value.trim();
        if (message && ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                message: message,
                sender_id: document.body.getAttribute('data-user-id'),
                sender_username: document.body.getAttribute('data-user-username')
            }));
            messageInput.value = '';
            console.log(document.body.getAttribute('data-user-id'))
        }
    });
});
