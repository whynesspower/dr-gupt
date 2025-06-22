document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const chatMessages = document.getElementById('chat-messages');
    const textInput = document.getElementById('text-input');
    const sendButton = document.getElementById('send-button');
    const recordButton = document.getElementById('record-button');
    const statusText = document.getElementById('status-text');

    // WebSocket connection
    let socket;
    let clientId = generateUUID();
    let isRecording = false;
    let mediaRecorder;
    let audioChunks = [];
    let stream;

    // Connect to WebSocket
    function connectWebSocket() {
        socket = new WebSocket(`ws://${window.location.host}/ws/${clientId}`);

        socket.onopen = () => {
            updateStatus('Connected');
            console.log('WebSocket connection established');
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };

        socket.onclose = () => {
            updateStatus('Disconnected. Reconnecting...');
            console.log('WebSocket connection closed. Attempting to reconnect...');
            setTimeout(connectWebSocket, 3000);
        };

        socket.onerror = (error) => {
            updateStatus('Connection error');
            console.error('WebSocket error:', error);
        };
    }

    // Handle WebSocket messages
    function handleWebSocketMessage(data) {
        switch (data.type) {
            case 'chat_response':
                addMessage(data.message, 'assistant');
                break;
            case 'speech_response':
                addMessage(data.transcript, 'user');
                addMessage(data.message, 'assistant');
                playAudio(data.audio);
                break;
            case 'error':
                updateStatus(`Error: ${data.message}`);
                addSystemMessage(`Error: ${data.message}`);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    // Add a message to the chat
    function addMessage(content, role) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = content;

        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = new Date().toLocaleTimeString();

        messageDiv.appendChild(messageContent);
        messageDiv.appendChild(messageTime);
        chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Add a system message
    function addSystemMessage(content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message system';

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = content;

        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Send a text message
    function sendTextMessage() {
        const message = textInput.value.trim();
        if (!message) return;

        addMessage(message, 'user');
        
        const data = {
            type: 'chat',
            message: message
        };

        socket.send(JSON.stringify(data));
        textInput.value = '';
        updateStatus('Processing...');
    }

    // Handle audio recording
    async function toggleRecording() {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    }

    // Start recording audio
    async function startRecording() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = sendAudioMessage;

            mediaRecorder.start();
            isRecording = true;
            recordButton.classList.add('recording');
            recordButton.querySelector('.record-text').textContent = 'Stop';
            updateStatus('Recording...');
        } catch (error) {
            console.error('Error accessing microphone:', error);
            updateStatus('Microphone access denied');
            addSystemMessage('Could not access microphone. Please check permissions.');
        }
    }

    // Stop recording audio
    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            stream.getTracks().forEach(track => track.stop());
            isRecording = false;
            recordButton.classList.remove('recording');
            recordButton.querySelector('.record-text').textContent = 'Record';
            updateStatus('Processing audio...');
        }
    }

    // Send recorded audio to server
    async function sendAudioMessage() {
        try {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const reader = new FileReader();
            
            reader.onloadend = () => {
                const base64Audio = reader.result.split(',')[1];
                
                const data = {
                    type: 'speech',
                    audio: base64Audio,
                    language_code: 'en-IN',
                    target_language_code: 'en-IN'
                };
                
                socket.send(JSON.stringify(data));
            };
            
            reader.readAsDataURL(audioBlob);
        } catch (error) {
            console.error('Error sending audio:', error);
            updateStatus('Error sending audio');
            addSystemMessage('Error sending audio. Please try again.');
        }
    }

    // Play audio from base64 string
    function playAudio(base64Audio) {
        const audio = new Audio(`data:audio/wav;base64,${base64Audio}`);
        audio.play().catch(error => {
            console.error('Error playing audio:', error);
        });
    }

    // Update status indicator
    function updateStatus(message) {
        statusText.textContent = message;
    }

    // Generate a UUID for client identification
    function generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    // Event listeners
    sendButton.addEventListener('click', sendTextMessage);
    
    textInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendTextMessage();
        }
    });
    
    recordButton.addEventListener('click', toggleRecording);

    // Initialize WebSocket connection
    connectWebSocket();
});
