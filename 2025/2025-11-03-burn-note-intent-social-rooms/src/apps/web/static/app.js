// API base URL
const API_BASE = '/v1';

// Global state
let currentRoom = null;
let currentSession = null;
let wsClient = null;

// WebSocket Client
class WebSocketClient {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 1000; // Start with 1 second
        this.heartbeatInterval = null;
        this.isManualClose = false;
    }

    connect(sessionId) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            return;
        }

        this.isManualClose = false;
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/v1/ws?session_id=${encodeURIComponent(sessionId)}`;
        
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            this.reconnectAttempts = 0;
            this.reconnectDelay = 1000;
            this.startHeartbeat();
            
            // Subscribe to room events
            if (currentRoom) {
                this.subscribe(currentRoom.id);
            }
        };

        this.ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                this.handleMessage(message);
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error, event.data);
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        this.ws.onclose = () => {
            this.stopHeartbeat();
            
            if (!this.isManualClose && this.reconnectAttempts < this.maxReconnectAttempts) {
                this.reconnectAttempts++;
                const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), 30000);
                setTimeout(() => {
                    if (currentSession && currentSession.id) {
                        this.connect(currentSession.id);
                    }
                }, delay);
            }
        };
    }

    subscribe(roomId, whisperId = null, subscriptions = ['message', 'post', 'member', 'whisper']) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            console.warn('Cannot subscribe: WebSocket not connected');
            return;
        }

        const message = {
            type: 'subscribe',
            payload: {
                room_id: roomId,
                whisper_id: whisperId,
                subscriptions: subscriptions,
            }
        };

        this.ws.send(JSON.stringify(message));
    }

    unsubscribe(roomId = null, whisperId = null, subscriptions = []) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            return;
        }

        const message = {
            type: 'unsubscribe',
            payload: {
                room_id: roomId,
                whisper_id: whisperId,
                subscriptions: subscriptions,
            }
        };

        this.ws.send(JSON.stringify(message));
    }

    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                const message = {
                    type: 'ping',
                    payload: {
                        timestamp: new Date().toISOString(),
                    }
                };
                this.ws.send(JSON.stringify(message));
            }
        }, 30000); // Every 30 seconds
    }

    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }

    handleMessage(message) {
        switch (message.type) {
            case 'message':
                this.handleMessageCreated(message.payload);
                break;
            case 'whisper_message':
                this.handleWhisperMessage(message.payload);
                break;
            case 'member_joined':
                this.handleMemberJoined(message.payload);
                break;
            case 'member_left':
                this.handleMemberLeft(message.payload);
                break;
            case 'whisper_created':
                this.handleWhisperCreated(message.payload);
                break;
            case 'whisper_accepted':
                this.handleWhisperAccepted(message.payload);
                break;
            case 'whisper_declined':
                this.handleWhisperDeclined(message.payload);
                break;
            case 'whisper_ended':
                this.handleWhisperEnded(message.payload);
                break;
            case 'post_created':
                this.handlePostCreated(message.payload);
                break;
            case 'post_replied':
                this.handlePostReplied(message.payload);
                break;
            case 'subscription_confirmed':
                // Subscription confirmed
                break;
            case 'pong':
                // Heartbeat response
                break;
            case 'error':
                console.error('WebSocket error:', message.payload);
                break;
            default:
                console.warn('Unknown WebSocket message type:', message.type);
        }
    }

    handleMessageCreated(payload) {
        if (!currentRoom || payload.room_id !== currentRoom.id) return;
        if (payload.type === 'whisper') return; // Whisper messages handled separately
        
        const messagesContainer = document.getElementById('messages-container');
        if (messagesContainer) {
            const messageEl = createMessageElement(payload);
            messagesContainer.appendChild(messageEl);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        // Update active members
        if (payload.sender_mask !== currentSession?.mask) {
            activeMembers.add(payload.sender_mask);
            updateMembersListFromMessages();
        }
    }

    handleWhisperMessage(payload) {
        // Handle whisper messages - update chat if this whisper is currently open
        if (!payload.whisper_id) {
            console.warn('Whisper message missing whisper_id:', payload);
            return;
        }
        
        // Convert both to strings for comparison to avoid type mismatches
        const currentWhisperId = currentWhisper?.id ? String(currentWhisper.id) : null;
        const payloadWhisperId = String(payload.whisper_id);
        
        if (currentWhisper && currentWhisperId === payloadWhisperId) {
            // This message is for the currently open whisper chat
            const messagesContainer = document.getElementById('whisper-chat-messages');
            if (messagesContainer) {
                // Check if message already exists to avoid duplicates
                const existingMessage = messagesContainer.querySelector(`[data-message-id="${payload.id}"]`);
                if (existingMessage) {
                    return;
                }
                
                const messageEl = createWhisperMessageElement({
                    id: payload.id,
                    sender_mask: payload.sender_mask,
                    body: payload.body,
                    created_at: payload.created_at,
                });
                messagesContainer.appendChild(messageEl);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            } else {
                console.warn('Whisper chat messages container not found');
            }
        }
    }

    handleMemberJoined(payload) {
        if (!currentRoom || payload.room_id !== currentRoom.id) return;
        if (payload.mask === currentSession?.mask) return; // Don't add ourselves
        
        activeMembers.add(payload.mask);
        updateMembersListFromMessages();
    }

    handleMemberLeft(payload) {
        if (!currentRoom || payload.room_id !== currentRoom.id) return;
        
        activeMembers.delete(payload.mask);
        updateMembersListFromMessages();
    }

    handleWhisperCreated(payload) {
        // Update whispers list - add new whisper if it's for this user
        if (payload.whisper) {
            const whisper = payload.whisper;
            if (whisper.sender_mask === currentSession?.mask || whisper.recipient_mask === currentSession?.mask) {
                // Reload whispers list to show new whisper
                if (typeof loadWhispers === 'function') {
                    loadWhispers();
                }
            }
        }
    }

    handleWhisperAccepted(payload) {
        // Update the whisper in the list if it's currently displayed
        if (payload.whisper) {
            const whisper = payload.whisper;
            if (whisper.sender_mask === currentSession?.mask || whisper.recipient_mask === currentSession?.mask) {
                // Reload whispers list to update state
                if (typeof loadWhispers === 'function') {
                    loadWhispers();
                }
                
                // If this whisper is currently open, subscribe to it
                if (currentWhisper && currentWhisper.id === whisper.id && whisper.state === 'active') {
                    this.subscribe(currentRoom.id, whisper.id);
                }
            }
        }
    }

    handleWhisperDeclined(payload) {
        // Update whisper in list
        if (typeof loadWhispers === 'function') {
            loadWhispers();
        }
    }

    handleWhisperEnded(payload) {
        // Update whisper in list
        if (typeof loadWhispers === 'function') {
            loadWhispers();
        }
        
        // If this was the currently open whisper, close it
        if (currentWhisper && currentWhisper.id === payload.whisper_id) {
            currentWhisper = null;
            document.getElementById('whisper-chat-header').style.display = 'none';
            document.getElementById('whisper-chat-input-area').style.display = 'none';
            document.getElementById('whisper-chat-messages').innerHTML = '<p class="empty">Select a whisper to view messages</p>';
        }
    }

    handlePostCreated(payload) {
        // Handle post creation - refresh posts list if on posts tab
        if (typeof loadPosts === 'function') {
            loadPosts();
        }
    }

    handlePostReplied(payload) {
        // Handle post reply - refresh posts list if on posts tab
        if (typeof loadPosts === 'function') {
            loadPosts();
        }
    }

    disconnect() {
        this.isManualClose = true;
        this.stopHeartbeat();
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}

// Fetch and display rooms
async function loadRooms() {
    try {
        const response = await fetch(`${API_BASE}/rooms`);
        const data = await response.json();
        
        const roomsContainer = document.getElementById('rooms-container');
        roomsContainer.innerHTML = '';
        
        if (data.items && data.items.length > 0) {
            data.items.forEach(room => {
                const roomCard = createRoomCard(room);
                roomsContainer.appendChild(roomCard);
            });
        } else {
            roomsContainer.innerHTML = '<p>No rooms available</p>';
        }
    } catch (error) {
        console.error('Failed to load rooms:', error);
        document.getElementById('rooms-container').innerHTML = 
            '<p class="error">Failed to load rooms. Please refresh the page.</p>';
    }
}

// Create a room card element
function createRoomCard(room) {
    const card = document.createElement('div');
    card.className = 'room-card';
    card.innerHTML = `
        <h3>${escapeHtml(room.title)}</h3>
        <p class="room-meta">Language: ${room.language} | Created: ${formatDate(room.created_at)}</p>
        <button class="join-btn" onclick="joinRoom('${room.id}', '${escapeHtml(room.title)}')">
            Join Room
        </button>
    `;
    return card;
}

// Join a room
async function joinRoom(roomId, roomTitle) {
    try {
        const response = await fetch(`${API_BASE}/rooms/${roomId}/join`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ttl_hours: 24 }),
        });
        
        if (!response.ok) {
            // Try to parse error response
            let errorMessage = 'Failed to join room. Please try again.';
            try {
                const errorData = await response.json();
                errorMessage = errorData.message || errorMessage;
                console.error('Join room error:', errorData);
            } catch (e) {
                // If response isn't JSON, use status text
                errorMessage = `Failed to join room: ${response.status} ${response.statusText}`;
            }
            throw new Error(errorMessage);
        }
        
        const data = await response.json();
        currentRoom = { id: roomId, title: roomTitle };
        currentSession = {
            id: data.session_id,
            mask: data.session_mask,
        };
        
        // Connect WebSocket
        if (!wsClient) {
            wsClient = new WebSocketClient();
        }
        wsClient.connect(data.session_id);
        
        // Update session controls and switch to room view
        updateSessionControls();
        showRoomView();
        loadMessages();
    } catch (error) {
        console.error('Failed to join room:', error);
        alert(error.message || 'Failed to join room. Please try again.');
    }
}

// Show room view
function showRoomView() {
    document.getElementById('intent-view').style.display = 'none';
    document.getElementById('rooms-view').style.display = 'none';
    document.getElementById('room-view').style.display = 'block';
    document.getElementById('room-title').textContent = currentRoom.title;
    document.getElementById('session-mask').textContent = `Your mask: ${currentSession.mask}`;
    
    // Load active members when entering room (initial load)
    loadActiveMembers();
    
    // Note: Active members updates now come via WebSocket member_joined/member_left events
    // No polling needed
}

// Show rooms view
function showRoomsView() {
    document.getElementById('intent-view').style.display = 'none';
    document.getElementById('room-view').style.display = 'none';
    document.getElementById('rooms-view').style.display = 'block';
    loadRooms();
}

// Load messages for current room
let activeMembers = new Set();

async function loadMessages() {
    if (!currentRoom) return;
    
    try {
        const response = await fetch(`${API_BASE}/messages?room_id=${currentRoom.id}`);
        const data = await response.json();
        
        const messagesContainer = document.getElementById('messages-container');
        messagesContainer.innerHTML = '';
        
        // Reset active members set
        activeMembers.clear();
        
        if (data.items && data.items.length > 0) {
            data.items.forEach(msg => {
                // Filter out whisper messages from Live tab
                if (msg.type !== 'whisper') {
                    const messageEl = createMessageElement(msg);
                    messagesContainer.appendChild(messageEl);
                }
                // Track active members (excluding whispers)
                if (msg.type !== 'whisper' && msg.sender_mask !== currentSession?.mask) {
                    activeMembers.add(msg.sender_mask);
                }
            });
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        } else {
            messagesContainer.innerHTML = '<p class="empty">No messages yet. Be the first to send one!</p>';
        }
        
        // Always update members list after loading messages
        loadActiveMembers();
    } catch (error) {
        console.error('Failed to load messages:', error);
    }
}

// Load active members from API (sessions)
async function loadActiveMembers() {
    if (!currentRoom) {
        console.warn('loadActiveMembers: No currentRoom');
        return;
    }
    
    const membersList = document.getElementById('members-list');
    if (!membersList) {
        console.warn('loadActiveMembers: members-list element not found');
        return;
    }
    
    const url = `${API_BASE}/rooms/${currentRoom.id}/members`;
    
    try {
        const response = await fetch(url);
        
        if (!response.ok) {
            const errorText = await response.text().catch(() => 'Unknown error');
            console.error('Failed to load active members:', response.status, errorText);
            
            // Show user-friendly error
            membersList.innerHTML = '<p style="font-size: 0.85rem; color: #e74c3c;">Failed to load members. Using message-based list.</p>';
            
            // Fallback to message-based list after short delay
            setTimeout(() => {
                updateMembersListFromMessages();
            }, 1000);
            return;
        }
        
        const data = await response.json();
        const allMembers = (data.items || []).map(m => m.mask);
        
        // Filter out current user's mask
        const otherMembers = allMembers.filter(mask => mask !== currentSession?.mask);
        
        // Also add members from messages (for backward compatibility)
        Array.from(activeMembers).forEach(mask => {
            if (mask !== 'System' && mask !== currentSession?.mask && !otherMembers.includes(mask)) {
                otherMembers.push(mask);
            }
        });
        
        if (otherMembers.length === 0) {
            membersList.innerHTML = '<p style="font-size: 0.85rem; color: #999;">No other members active</p>';
            return;
        }
        membersList.innerHTML = '';
        otherMembers.forEach(mask => {
            const memberItem = document.createElement('div');
            memberItem.className = 'member-item';
            
            const memberName = document.createElement('span');
            memberName.className = 'member-name';
            memberName.textContent = mask;
            
            const whisperBtn = document.createElement('button');
            whisperBtn.className = 'whisper-btn';
            whisperBtn.textContent = 'Whisper';
            whisperBtn.onclick = () => requestWhisper(mask);
            
            memberItem.appendChild(memberName);
            memberItem.appendChild(whisperBtn);
            membersList.appendChild(memberItem);
        });
    } catch (error) {
        console.error('Exception loading active members:', error);
        membersList.innerHTML = '<p style="font-size: 0.85rem; color: #e74c3c;">Error loading members. Check console.</p>';
        // Fallback to message-based list
        setTimeout(() => {
            updateMembersListFromMessages();
        }, 1000);
    }
}

// Update members list in Live tab (fallback - from messages)
function updateMembersListFromMessages() {
    const membersList = document.getElementById('members-list');
    if (!membersList) return;
    
    // Filter out "System" and current user's mask
    const otherMembers = Array.from(activeMembers).filter(mask => 
        mask !== 'System' && mask !== currentSession?.mask
    );
    
    if (otherMembers.length === 0) {
        membersList.innerHTML = '<p style="font-size: 0.85rem; color: #999;">No other members active</p>';
        return;
    }
    
    membersList.innerHTML = '';
    otherMembers.forEach(mask => {
        const memberItem = document.createElement('div');
        memberItem.className = 'member-item';
        
        const memberName = document.createElement('span');
        memberName.className = 'member-name';
        memberName.textContent = mask;
        
        const whisperBtn = document.createElement('button');
        whisperBtn.className = 'whisper-btn';
        whisperBtn.textContent = 'Whisper';
        whisperBtn.onclick = () => requestWhisper(mask);
        
        memberItem.appendChild(memberName);
        memberItem.appendChild(whisperBtn);
        membersList.appendChild(memberItem);
    });
}

// Legacy function name for backward compatibility
function updateMembersList() {
    loadActiveMembers();
}

// Create a message element
function createMessageElement(msg) {
    const messageEl = document.createElement('div');
    messageEl.className = 'message';
    messageEl.id = `message-${msg.id}`;
    messageEl.dataset.messageId = msg.id;
    messageEl.innerHTML = `
        <div class="message-header">
            <span class="sender-mask">${escapeHtml(msg.sender_mask)}</span>
            <span class="message-time">${formatDate(msg.created_at)}</span>
        </div>
        <div class="message-body">${escapeHtml(msg.body)}</div>
    `;
    return messageEl;
}

// Send a message
async function sendMessage() {
    if (!currentRoom || !currentSession) {
        alert('Please join a room first');
        return;
    }
    
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value.trim();
    
    if (!message) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/messages`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                room_id: currentRoom.id,
                sender_mask: currentSession.mask,
                type: 'text',
                body: message,
            }),
        });
        
        if (!response.ok) {
            throw new Error(`Failed to send message: ${response.statusText}`);
        }
        
        messageInput.value = '';
        // Reload messages
        setTimeout(loadMessages, 100);
    } catch (error) {
        console.error('Failed to send message:', error);
        alert('Failed to send message. Please try again.');
    }
}

// Match intent and show results
async function matchIntent() {
    const intentInput = document.getElementById('intent-input');
    const intent = intentInput.value.trim();
    
    if (intent.length < 3) {
        alert('Please enter at least 3 characters');
        return;
    }
    
    const includeSensitive = document.getElementById('include-sensitive').checked;
    
    try {
        const response = await fetch(`${API_BASE}/intent/match`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ intent, include_sensitive: includeSensitive }),
        });
        
        if (!response.ok) {
            throw new Error('Failed to match intent');
        }
        
        const data = await response.json();
        displayMatchedRooms(data.rooms, data.alternatives);
    } catch (error) {
        console.error('Failed to match intent:', error);
        alert('Failed to find matching rooms. Please try again.');
    }
}

// Display matched rooms
function displayMatchedRooms(rooms, alternatives) {
    // Hide intent entry, show results
    document.querySelector('.intent-entry').style.display = 'none';
    document.getElementById('matched-results').style.display = 'block';
    
    const container = document.getElementById('matched-rooms-container');
    container.innerHTML = '';
    
    if (rooms.length === 0) {
        container.innerHTML = '<p>No matching rooms found. Try different keywords.</p>';
        return;
    }
    
    // Check if this is a newly created room
    if (rooms.length === 1 && rooms[0].score === 1.0 && rooms[0].reason.includes("New room created")) {
        container.innerHTML = `
            <div class="new-room-notice">
                <h3>✨ We created a fresh space for your interest</h3>
                <p>You'll be the first person in this room. Others with similar interests will join soon.</p>
            </div>
        `;
        
        const card = createMatchedRoomCard(rooms[0]);
        container.appendChild(card);
        
        // Don't show alternatives for new rooms
        document.getElementById('alternatives-section').style.display = 'none';
        return;
    }
    
    rooms.forEach(match => {
        const card = createMatchedRoomCard(match);
        container.appendChild(card);
    });
    
    // Handle alternatives
    if (alternatives && alternatives.length > 0) {
        document.getElementById('alternatives-section').style.display = 'block';
        document.getElementById('alternatives-count').textContent = `(${alternatives.length})`;
        
        const altContainer = document.getElementById('alternatives-container');
        altContainer.innerHTML = '';
        alternatives.forEach(match => {
            const card = createMatchedRoomCard(match);
            altContainer.appendChild(card);
        });
    } else {
        document.getElementById('alternatives-section').style.display = 'none';
    }
}

// Create a matched room card element
function createMatchedRoomCard(match) {
    const card = document.createElement('div');
    card.className = 'room-card matched-room-card';
    
    // Map score to qualitative indicator
    let fitIndicator = '';
    if (match.score >= 0.80) {
        fitIndicator = '<span class="fit-badge excellent">Excellent Match</span>';
    } else if (match.score >= 0.60) {
        fitIndicator = '<span class="fit-badge good">Good Fit</span>';
    } else if (match.score >= 0.40) {
        fitIndicator = '<span class="fit-badge moderate">Worth Exploring</span>';
    }
    
    card.innerHTML = `
        <div>
            <h3>${escapeHtml(match.room.title)}${fitIndicator}</h3>
            <p class="match-reason">${escapeHtml(match.reason)}</p>
            <p class="room-meta">Language: ${match.room.language} | Members: ${match.room.member_count}</p>
        </div>
        <button class="join-btn" onclick="joinRoom('${match.room.id}', '${escapeHtml(match.room.title)}')">Join Room</button>
    `;
    return card;
}

// View navigation functions
function showIntentView() {
    document.getElementById('rooms-view').style.display = 'none';
    document.getElementById('room-view').style.display = 'none';
    document.getElementById('intent-view').style.display = 'block';
    showIntentEntry();
}

function showIntentEntry() {
    document.querySelector('.intent-entry').style.display = 'block';
    document.getElementById('matched-results').style.display = 'none';
    // Clear the input
    document.getElementById('intent-input').value = '';
}

function toggleAlternatives() {
    const container = document.getElementById('alternatives-container');
    const toggleText = document.getElementById('alternatives-toggle-text');
    
    if (container.style.display === 'none') {
        container.style.display = 'block';
        toggleText.textContent = 'Hide options';
    } else {
        container.style.display = 'none';
        toggleText.textContent = 'Show more options';
    }
}

// Session management functions
function updateSessionControls() {
    const controls = document.getElementById('session-controls');
    if (currentSession) {
        controls.style.display = 'flex';
    } else {
        controls.style.display = 'none';
    }
}

async function burnSession() {
    if (!currentSession) return;
    
    if (!confirm('Are you sure you want to burn your session? This cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/sessions/${currentSession.id}`, {
            method: 'DELETE',
            headers: { 'X-Session-Id': currentSession.id },
        });
        
        if (response.ok || response.status === 404) {
            currentSession = null;
            currentRoom = null;
            updateSessionControls();
            showIntentView();
            alert('Session burned successfully');
        } else {
            throw new Error('Failed to burn session');
        }
    } catch (error) {
        console.error('Failed to burn session:', error);
        alert('Failed to burn session. Please try again.');
    }
}

function leaveRoom() {
    // Disconnect WebSocket
    if (wsClient) {
        wsClient.disconnect();
        wsClient = null;
    }
    
    currentRoom = null;
    showIntentView();
}

// Handle Enter key in message input
document.addEventListener('DOMContentLoaded', () => {
    const messageInput = document.getElementById('message-input');
    if (messageInput) {
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
    
    // Handle Enter key in intent input
    const intentInput = document.getElementById('intent-input');
    if (intentInput) {
        intentInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                matchIntent();
            }
        });
    }
    
    // Initialize: show intent view on page load
    showIntentView();
});

// Tab switching
function switchTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected tab content
    const content = document.getElementById(`tab-${tabName}-content`);
    if (content) {
        content.classList.add('active');
    } else {
        console.error(`Tab content element not found: tab-${tabName}-content`);
    }
    
    // Add active class to selected tab
    const tab = document.getElementById(`tab-${tabName}`);
    if (tab) {
        tab.classList.add('active');
    } else {
        console.error(`Tab button not found: tab-${tabName}`);
    }
    
    // Load content if switching to posts, highlights, resources, or whispers tab
    if (tabName === 'posts' && currentRoom) {
        loadPosts();
    } else if (tabName === 'highlights' && currentRoom) {
        loadHighlights();
    } else if (tabName === 'resources' && currentRoom) {
        loadResources();
    } else if (tabName === 'whispers' && currentRoom) {
        // Small delay to ensure DOM is ready
        setTimeout(() => {
            loadWhispers();
        }, 50);
    }
}

// Global state for highlights
let highlightsLast24h = false;

// Load highlights for current room
async function loadHighlights() {
    if (!currentRoom) return;
    
    try {
        const url = `${API_BASE}/rooms/${currentRoom.id}/highlights?last_24h=${highlightsLast24h}`;
        const response = await fetch(url);
        const data = await response.json();
        
        const highlightsContainer = document.getElementById('highlights-container');
        highlightsContainer.innerHTML = '';
        
        if (data.items && data.items.length > 0) {
            data.items.forEach(highlight => {
                const highlightEl = createHighlightElement(highlight);
                highlightsContainer.appendChild(highlightEl);
            });
        } else {
            highlightsContainer.innerHTML = '<p class="empty">No highlights yet. Create one to help others catch up!</p>';
        }
    } catch (error) {
        console.error('Failed to load highlights:', error);
        document.getElementById('highlights-container').innerHTML = 
            '<p class="error">Failed to load highlights. Please refresh the page.</p>';
    }
}

// Create a highlight element
function createHighlightElement(highlight) {
    const highlightEl = document.createElement('div');
    highlightEl.className = `highlight-card ${highlight.is_auto ? 'auto' : ''}`;
    highlightEl.id = `highlight-${highlight.id}`;
    
    const referenceSection = highlight.reference_id ? `
        <div class="highlight-reference">
            <a href="#" class="highlight-reference-link" onclick="viewReference('${highlight.reference_type}', '${highlight.reference_id}'); return false;">
                View ${highlight.reference_type === 'post' ? 'Post' : 'Message'}
            </a>
        </div>
    ` : '';
    
    const deleteBtn = (highlight.curator_mask === 'anonymous' || highlight.curator_mask === 'system') ? `
        <button class="highlight-delete-btn" onclick="deleteHighlight('${highlight.id}')">Delete</button>
    ` : '';
    
    highlightEl.innerHTML = `
        <div class="highlight-card-header">
            <div style="flex: 1;">
                <div class="highlight-title">${escapeHtml(highlight.title)}</div>
                <div class="highlight-meta">
                    ${highlight.is_auto ? '<span class="highlight-auto-badge">Auto</span>' : ''}
                    <span>by ${escapeHtml(highlight.curator_mask)}</span>
                    <span class="message-time">${formatDate(highlight.created_at)}</span>
                </div>
            </div>
        </div>
        ${referenceSection}
        ${deleteBtn ? `<div class="highlight-actions">${deleteBtn}</div>` : ''}
    `;
    
    return highlightEl;
}

// Toggle last 24h filter
function toggleLast24h() {
    highlightsLast24h = !highlightsLast24h;
    const toggle = document.getElementById('last24h-toggle');
    toggle.textContent = highlightsLast24h ? 'Show all' : 'Skim last 24h';
    loadHighlights();
}

// Toggle create highlight form
function toggleCreateHighlightForm() {
    const form = document.getElementById('create-highlight-form');
    if (form.style.display === 'none') {
        form.style.display = 'block';
        document.getElementById('highlight-title-input').focus();
    } else {
        form.style.display = 'none';
        document.getElementById('highlight-title-input').value = '';
        document.getElementById('highlight-reference-id-input').value = '';
        document.getElementById('highlight-reference-type').value = 'standalone';
        document.getElementById('highlight-reference-id-input').style.display = 'none';
    }
}

// Handle reference type change
document.addEventListener('DOMContentLoaded', () => {
    const referenceTypeSelect = document.getElementById('highlight-reference-type');
    const referenceIdInput = document.getElementById('highlight-reference-id-input');
    
    if (referenceTypeSelect && referenceIdInput) {
        referenceTypeSelect.addEventListener('change', () => {
            if (referenceTypeSelect.value === 'standalone') {
                referenceIdInput.style.display = 'none';
            } else {
                referenceIdInput.style.display = 'block';
                referenceIdInput.placeholder = `Enter ${referenceTypeSelect.value} ID...`;
            }
        });
    }
});

// Submit highlight creation
async function submitHighlight() {
    if (!currentRoom || !currentSession) {
        alert('Please join a room first');
        return;
    }
    
    const titleInput = document.getElementById('highlight-title-input');
    const referenceTypeSelect = document.getElementById('highlight-reference-type');
    const referenceIdInput = document.getElementById('highlight-reference-id-input');
    
    const title = titleInput.value.trim();
    if (!title) {
        alert('Please enter a highlight title');
        return;
    }
    
    const referenceType = referenceTypeSelect.value;
    const referenceId = referenceType !== 'standalone' ? referenceIdInput.value.trim() : null;
    
    if (referenceType !== 'standalone' && !referenceId) {
        alert(`Please enter a ${referenceType} ID`);
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/rooms/${currentRoom.id}/highlights`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: title,
                reference_type: referenceType,
                reference_id: referenceId,
            }),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to create highlight');
        }
        
        // Clear form and reload highlights
        toggleCreateHighlightForm();
        loadHighlights();
    } catch (error) {
        console.error('Failed to create highlight:', error);
        alert(`Failed to create highlight: ${error.message}`);
    }
}

// Delete highlight
async function deleteHighlight(highlightId) {
    if (!confirm('Are you sure you want to delete this highlight?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/highlights/${highlightId}`, {
            method: 'DELETE',
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete highlight');
        }
        
        // Remove from UI
        const highlightEl = document.getElementById(`highlight-${highlightId}`);
        if (highlightEl) {
            highlightEl.remove();
        }
        
        // Reload to ensure consistency
        loadHighlights();
    } catch (error) {
        console.error('Failed to delete highlight:', error);
        alert('Failed to delete highlight. Please try again.');
    }
}

// View referenced message or post
async function viewReference(referenceType, referenceId) {
    if (referenceType === 'post') {
        // Switch to Posts tab and scroll to the post
        switchTab('posts');
        // Wait a bit for posts to load, then try to scroll to the post
        setTimeout(() => {
            const postEl = document.getElementById(`post-${referenceId}`);
            if (postEl) {
                postEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
                postEl.style.border = '3px solid #667eea';
                setTimeout(() => {
                    postEl.style.border = '';
                }, 2000);
            }
        }, 500);
    } else if (referenceType === 'message') {
        // Switch to Live tab and try to find the message
        switchTab('live');
        setTimeout(() => {
            const messages = document.querySelectorAll('.message');
            for (const msg of messages) {
                if (msg.id === `message-${referenceId}` || msg.dataset.messageId === referenceId) {
                    msg.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    msg.style.border = '3px solid #667eea';
                    setTimeout(() => {
                        msg.style.border = '';
                    }, 2000);
                    break;
                }
            }
        }, 500);
    }
}

// Global state for resources
let resourcesCurrentCategory = null;

// Load resources for current room
async function loadResources(category = null) {
    if (!currentRoom) return;
    
    const resourcesContainer = document.getElementById('resources-container');
    if (!resourcesContainer) {
        console.warn('Resources container not found');
        return;
    }
    
    try {
        let url = `${API_BASE}/rooms/${currentRoom.id}/resources`;
        if (category) {
            url += `?category=${encodeURIComponent(category)}`;
        }
        const response = await fetch(url);
        
        // Check if response is successful before parsing JSON
        if (!response.ok) {
            const errorText = await response.text();
            let errorMessage = 'Failed to load resources';
            try {
                const errorData = JSON.parse(errorText);
                errorMessage = errorData.message || errorMessage;
            } catch (e) {
                // If error response isn't JSON, use the text or status
                errorMessage = errorText || `Server returned ${response.status}`;
            }
            console.error('Failed to load resources:', response.status, errorMessage);
            resourcesContainer.innerHTML = `<p class="error">${escapeHtml(errorMessage)}</p>`;
            return;
        }
        
        const data = await response.json();
        
        resourcesContainer.innerHTML = '';
        
        if (data.items && data.items.length > 0) {
            // Update category filter dropdown
            updateCategoryFilter(data.items);
            
            data.items.forEach(resource => {
                try {
                    const resourceEl = createResourceElement(resource);
                    resourcesContainer.appendChild(resourceEl);
                } catch (error) {
                    console.error('Failed to create resource element:', error, resource);
                    // Continue with other resources even if one fails
                }
            });
        } else {
            resourcesContainer.innerHTML = '<p class="empty">No resources yet. Create one to help others find useful links!</p>';
        }
    } catch (error) {
        console.error('Failed to load resources:', error);
        if (resourcesContainer) {
            resourcesContainer.innerHTML = 
                '<p class="error">Failed to load resources. Please refresh the page.</p>';
        }
    }
}

// Update category filter dropdown with available categories
function updateCategoryFilter(resources) {
    const filter = document.getElementById('resource-category-filter');
    if (!filter) return;
    
    // Get unique categories from resources
    const categories = new Set();
    resources.forEach(resource => {
        if (resource.category) {
            categories.add(resource.category);
        }
    });
    
    // Clear existing options except "All Categories"
    filter.innerHTML = '<option value="">All Categories</option>';
    
    // Add category options
    Array.from(categories).sort().forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        filter.appendChild(option);
    });
}

// Create a resource element
function createResourceElement(resource) {
    const resourceEl = document.createElement('div');
    resourceEl.className = `resource-card ${resource.is_verified ? 'verified' : ''}`;
    resourceEl.id = `resource-${resource.id}`;
    
    const descriptionSection = resource.description ? `
        <div class="resource-description">${escapeHtml(resource.description)}</div>
    ` : '';
    
    const categoryBadge = resource.category ? `
        <span class="resource-category-badge">${escapeHtml(resource.category)}</span>
    ` : '';
    
    const verifiedBadge = resource.is_verified ? `
        <span class="resource-verified-badge">Verified</span>
    ` : '';
    
    const actions = (resource.curator_mask === 'anonymous' || resource.curator_mask === 'system') ? `
        <div class="resource-actions">
            <button class="resource-edit-btn" onclick="editResource('${resource.id}')">Edit</button>
            <button class="resource-delete-btn" onclick="deleteResource('${resource.id}')">Delete</button>
        </div>
    ` : '';
    
    resourceEl.innerHTML = `
        <div class="resource-card-header">
            <div style="flex: 1;">
                <div class="resource-title">${escapeHtml(resource.title)}</div>
                <a href="${escapeHtml(resource.url)}" target="_blank" rel="noopener noreferrer" class="resource-url">
                    ${escapeHtml(resource.url)}
                </a>
                <div class="resource-meta">
                    ${verifiedBadge}
                    ${categoryBadge}
                    <span>by ${escapeHtml(resource.curator_mask)}</span>
                    <span class="message-time">${formatDate(resource.created_at)}</span>
                </div>
            </div>
        </div>
        ${descriptionSection}
        ${actions}
    `;
    
    return resourceEl;
}

// Filter resources by category
function filterResourcesByCategory() {
    const filter = document.getElementById('resource-category-filter');
    if (!filter) return;
    
    const category = filter.value || null;
    resourcesCurrentCategory = category;
    loadResources(category);
}

// Toggle create resource form
function toggleCreateResourceForm() {
    const form = document.getElementById('create-resource-form');
    if (form.style.display === 'none') {
        form.style.display = 'block';
        document.getElementById('resource-title-input').focus();
    } else {
        form.style.display = 'none';
        document.getElementById('resource-title-input').value = '';
        document.getElementById('resource-url-input').value = '';
        document.getElementById('resource-description-input').value = '';
        document.getElementById('resource-category-input').value = '';
    }
}

// Submit resource creation
async function submitResource() {
    if (!currentRoom || !currentSession) {
        alert('Please join a room first');
        return;
    }
    
    const titleInput = document.getElementById('resource-title-input');
    const urlInput = document.getElementById('resource-url-input');
    const descriptionInput = document.getElementById('resource-description-input');
    const categoryInput = document.getElementById('resource-category-input');
    
    const title = titleInput.value.trim();
    const url = urlInput.value.trim();
    const description = descriptionInput.value.trim() || null;
    const category = categoryInput.value.trim() || null;
    
    if (!title) {
        alert('Please enter a resource title');
        return;
    }
    
    if (!url) {
        alert('Please enter a URL');
        return;
    }
    
    // Basic URL validation
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        alert('URL must start with http:// or https://');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/rooms/${currentRoom.id}/resources`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: title,
                url: url,
                description: description,
                category: category,
            }),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to create resource');
        }
        
        // Clear form and reload resources
        toggleCreateResourceForm();
        loadResources(resourcesCurrentCategory);
    } catch (error) {
        console.error('Failed to create resource:', error);
        alert(`Failed to create resource: ${error.message}`);
    }
}

// Edit resource
async function editResource(resourceId) {
    // For MVP, we'll show a simple prompt-based edit
    // In a more robust version, this would show a modal with pre-filled form
    const resourceEl = document.getElementById(`resource-${resourceId}`);
    if (!resourceEl) return;
    
    const title = prompt('Enter new title:', resourceEl.querySelector('.resource-title').textContent);
    if (title === null) return;
    
    const url = prompt('Enter new URL:', resourceEl.querySelector('.resource-url').textContent.trim());
    if (url === null) return;
    
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        alert('URL must start with http:// or https://');
        return;
    }
    
    const description = prompt('Enter new description (optional):', resourceEl.querySelector('.resource-description')?.textContent.trim() || '');
    
    const category = prompt('Enter new category (optional):', resourceEl.querySelector('.resource-category-badge')?.textContent.trim() || '');
    
    try {
        const response = await fetch(`${API_BASE}/resources/${resourceId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: title,
                url: url,
                description: description || null,
                category: category || null,
            }),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to update resource');
        }
        
        // Reload resources
        loadResources(resourcesCurrentCategory);
    } catch (error) {
        console.error('Failed to update resource:', error);
        alert(`Failed to update resource: ${error.message}`);
    }
}

// Delete resource
async function deleteResource(resourceId) {
    if (!confirm('Are you sure you want to delete this resource?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/resources/${resourceId}`, {
            method: 'DELETE',
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete resource');
        }
        
        // Remove from UI
        const resourceEl = document.getElementById(`resource-${resourceId}`);
        if (resourceEl) {
            resourceEl.remove();
        }
        
        // Reload to ensure consistency
        loadResources(resourcesCurrentCategory);
    } catch (error) {
        console.error('Failed to delete resource:', error);
        alert('Failed to delete resource. Please try again.');
    }
}

// Load posts for current room
async function loadPosts() {
    if (!currentRoom) return;
    
    try {
        const response = await fetch(`${API_BASE}/posts?room_id=${currentRoom.id}`);
        const data = await response.json();
        
        const postsContainer = document.getElementById('posts-container');
        postsContainer.innerHTML = '';
        
        if (data.items && data.items.length > 0) {
            for (const post of data.items) {
                const postEl = await createPostElement(post);
                postsContainer.appendChild(postEl);
            }
        } else {
            postsContainer.innerHTML = '<p class="empty">No posts yet. Be the first to create one!</p>';
        }
    } catch (error) {
        console.error('Failed to load posts:', error);
        document.getElementById('posts-container').innerHTML = 
            '<p class="error">Failed to load posts. Please refresh the page.</p>';
    }
}

// Create a post element with replies
async function createPostElement(post) {
    const postEl = document.createElement('div');
    postEl.className = 'post';
    postEl.id = `post-${post.id}`;
    
    // Load replies for this post
    let replies = [];
    try {
        const repliesResponse = await fetch(`${API_BASE}/posts/${post.id}/replies`);
        const repliesData = await repliesResponse.json();
        replies = repliesData.items || [];
    } catch (error) {
        console.error(`Failed to load replies for post ${post.id}:`, error);
    }
    
    postEl.innerHTML = `
        <div class="post-header">
            <div class="post-meta">
                <span class="sender-mask">${escapeHtml(post.sender_mask)}</span>
                <span class="message-time">${formatDate(post.created_at)}</span>
            </div>
        </div>
        <div class="post-body">${escapeHtml(post.body)}</div>
        <div class="post-footer">
            <span class="reply-count">${post.reply_count || 0} ${post.reply_count === 1 ? 'reply' : 'replies'}</span>
            <button class="reply-btn" onclick="toggleReplyForm('${post.id}')">Reply</button>
        </div>
        <div id="replies-${post.id}" class="replies-section" style="display: ${replies.length > 0 ? 'block' : 'none'}">
            ${replies.map(reply => `
                <div class="reply">
                    <div class="reply-header">
                        <span class="sender-mask">${escapeHtml(reply.sender_mask)}</span>
                        <span class="message-time">${formatDate(reply.created_at)}</span>
                    </div>
                    <div class="reply-body">${escapeHtml(reply.body)}</div>
                </div>
            `).join('')}
        </div>
        <div id="reply-form-${post.id}" class="reply-form" style="display: none;">
            <textarea id="reply-input-${post.id}" placeholder="Write a reply..." maxlength="4096"></textarea>
            <button onclick="submitReply('${post.id}')">Submit Reply</button>
            <button onclick="toggleReplyForm('${post.id}')" style="background: #999; margin-left: 0.5rem;">Cancel</button>
        </div>
    `;
    
    return postEl;
}

// Toggle reply form for a post
function toggleReplyForm(postId) {
    const form = document.getElementById(`reply-form-${postId}`);
    if (form) {
        form.style.display = form.style.display === 'none' ? 'block' : 'none';
        if (form.style.display === 'block') {
            document.getElementById(`reply-input-${postId}`).focus();
        }
    }
}

// Submit a reply to a post
async function submitReply(postId) {
    if (!currentRoom || !currentSession) {
        alert('Please join a room first');
        return;
    }
    
    const replyInput = document.getElementById(`reply-input-${postId}`);
    const replyBody = replyInput.value.trim();
    
    if (!replyBody) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/posts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                room_id: currentRoom.id,
                sender_mask: currentSession.mask,
                body: replyBody,
                parent_post_id: postId,
            }),
        });
        
        if (!response.ok) {
            throw new Error(`Failed to create reply: ${response.statusText}`);
        }
        
        replyInput.value = '';
        toggleReplyForm(postId);
        
        // Reload posts to show the new reply
        loadPosts();
    } catch (error) {
        console.error('Failed to submit reply:', error);
        alert('Failed to submit reply. Please try again.');
    }
}

// Create a new post
async function createPost() {
    if (!currentRoom || !currentSession) {
        alert('Please join a room first');
        return;
    }
    
    const postInput = document.getElementById('post-input');
    const postBody = postInput.value.trim();
    
    if (!postBody) {
        alert('Please enter a post');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/posts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                room_id: currentRoom.id,
                sender_mask: currentSession.mask,
                body: postBody,
            }),
        });
        
        if (!response.ok) {
            throw new Error(`Failed to create post: ${response.statusText}`);
        }
        
        postInput.value = '';
        // Reload posts to show the new post
        loadPosts();
    } catch (error) {
        console.error('Failed to create post:', error);
        alert('Failed to create post. Please try again.');
    }
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Whisper functionality
let currentWhisper = null;
let whispersList = [];

// Request a whisper with a member
async function requestWhisper(recipientMask) {
    if (!currentRoom || !currentSession) {
        alert('Please join a room first');
        return;
    }
    
    if (recipientMask === currentSession.mask) {
        alert('Cannot whisper to yourself');
        return;
    }
    
    const requestBody = {
        sender_mask: currentSession.mask,
        recipient_mask: recipientMask,
        room_id: currentRoom.id,
    };
    
    try {
        const response = await fetch(`${API_BASE}/whispers`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Whisper request failed:', response.status, errorText);
            let errorMessage = 'Failed to request whisper';
            try {
                const errorData = JSON.parse(errorText);
                errorMessage = errorData.message || errorMessage;
            } catch (e) {
                errorMessage = errorText || `Server returned ${response.status}`;
            }
            alert(errorMessage);
            return;
        }
        
        const responseData = await response.json();
        
        // Switch to whispers tab and reload
        switchTab('whispers');
        // Small delay to ensure tab switch completes
        setTimeout(() => {
            loadWhispers();
        }, 100);
    } catch (error) {
        console.error('Failed to request whisper:', error);
        alert(error.message || 'Failed to request whisper. Please try again.');
    }
}

// Load whispers for current room
async function loadWhispers() {
    if (!currentRoom || !currentSession) {
        console.warn('Cannot load whispers: missing currentRoom or currentSession');
        return;
    }
    
    const whispersListEl = document.getElementById('whispers-list');
    if (!whispersListEl) {
        console.error('whispers-list element not found in DOM');
        return;
    }
    
    try {
        const url = `${API_BASE}/whispers?mask=${encodeURIComponent(currentSession.mask)}&room_id=${currentRoom.id}`;
        
        const response = await fetch(url);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Whispers API error:', response.status, errorText);
            whispersListEl.innerHTML = `<p class="error">Failed to load whispers (${response.status}). Check console for details.</p>`;
            return;
        }
        
        const data = await response.json();
        whispersList = data.items || [];
        
        whispersListEl.innerHTML = '';
        
        if (whispersList.length === 0) {
            whispersListEl.innerHTML = '<p class="empty">No whispers yet. Request a whisper from a member in the Live tab!</p>';
        } else {
            whispersList.forEach(whisper => {
                try {
                    const whisperEl = createWhisperElement(whisper);
                    whispersListEl.appendChild(whisperEl);
                } catch (error) {
                    console.error('Failed to create whisper element:', error, whisper);
                }
            });
        }
    } catch (error) {
        console.error('Failed to load whispers:', error);
        if (whispersListEl) {
            whispersListEl.innerHTML = `<p class="error">Failed to load whispers: ${error.message}</p>`;
        }
    }
}

// Create whisper list element
function createWhisperElement(whisper) {
    const whisperEl = document.createElement('div');
    whisperEl.className = `whisper-item ${whisper.state}`;
    whisperEl.id = `whisper-${whisper.id}`;
    whisperEl.onclick = () => openWhisperChat(whisper);
    
    const otherParticipant = whisper.sender_mask === currentSession.mask 
        ? whisper.recipient_mask 
        : whisper.sender_mask;
    
    const expiryDate = new Date(whisper.expires_at);
    const now = new Date();
    const hoursRemaining = (expiryDate - now) / (1000 * 60 * 60);
    const expiryText = hoursRemaining < 1 
        ? `<span class="expiry-warning">Expires in ${Math.round(hoursRemaining * 60)} minutes</span>`
        : `Expires in ${Math.round(hoursRemaining)} hours`;
    
    let actionsHtml = '';
    if (whisper.state === 'pending' && whisper.recipient_mask === currentSession.mask) {
        actionsHtml = `
            <div class="whisper-actions">
                <button class="whisper-action-btn accept" onclick="event.stopPropagation(); acceptWhisper('${whisper.id}')">Accept</button>
                <button class="whisper-action-btn decline" onclick="event.stopPropagation(); declineWhisper('${whisper.id}')">Decline</button>
            </div>
        `;
    }
    
    whisperEl.innerHTML = `
        <div class="whisper-header">
            <span class="whisper-participant">${escapeHtml(otherParticipant)}</span>
            <span class="whisper-state ${whisper.state}">${escapeHtml(whisper.state)}</span>
        </div>
        <div class="whisper-expiry">${expiryText}</div>
        ${actionsHtml}
    `;
    
    return whisperEl;
}

// Accept a whisper
async function acceptWhisper(whisperId) {
    try {
        const response = await fetch(`${API_BASE}/whispers/${whisperId}/accept`, {
            method: 'POST',
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || 'Failed to accept whisper');
        }
        
        const updatedWhisper = await response.json();
        
        // Validate response has required fields
        if (!updatedWhisper.id || !updatedWhisper.state || !updatedWhisper.expires_at) {
            console.error('Invalid whisper response structure:', updatedWhisper);
            throw new Error('Invalid response from server');
        }
        
        // Check state is active
        if (updatedWhisper.state !== 'active') {
            console.warn('Whisper state is not active after accept:', updatedWhisper.state);
            // Still try to open chat, but log warning
        }
        
        // Immediately open the chat view with the updated whisper
        try {
            await openWhisperChat(updatedWhisper);
        } catch (chatError) {
            console.error('Failed to open whisper chat:', chatError);
            // Fallback: reload whispers list
            await loadWhispers();
            alert('Whisper accepted, but failed to open chat. Please click the whisper to open it.');
        }
        
        // Reload whispers list to keep UI in sync
        await loadWhispers();
    } catch (error) {
        console.error('Failed to accept whisper:', error);
        alert(error.message || 'Failed to accept whisper. Please try again.');
    }
}

// Decline a whisper
async function declineWhisper(whisperId) {
    try {
        const response = await fetch(`${API_BASE}/whispers/${whisperId}/decline`, {
            method: 'POST',
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || 'Failed to decline whisper');
        }
        
        loadWhispers();
    } catch (error) {
        console.error('Failed to decline whisper:', error);
        alert(error.message || 'Failed to decline whisper. Please try again.');
    }
}

// Open whisper chat view
async function openWhisperChat(whisper) {
    // Validate whisper object has required fields
    if (!whisper || !whisper.id) {
        console.error('Invalid whisper object:', whisper);
        alert('Invalid whisper data');
        return;
    }
    
    // Check state - allow case-insensitive comparison
    const whisperState = (whisper.state || '').toLowerCase();
    if (whisperState !== 'active') {
        console.warn('Whisper state is not active:', whisperState);
        alert(`Whisper must be active to view messages (current state: ${whisperState})`);
        return;
    }
    
    if (!currentSession || !currentSession.mask) {
        console.error('No current session available');
        alert('Session not found. Please refresh the page.');
        return;
    }
    
    if (!whisper.sender_mask || !whisper.recipient_mask) {
        console.error('Whisper missing sender_mask or recipient_mask:', whisper);
        alert('Invalid whisper data: missing participant information');
        return;
    }
    
    // Unsubscribe from previous whisper if switching
    if (currentWhisper && currentWhisper.id !== whisper.id && wsClient) {
        wsClient.unsubscribe(currentRoom.id, currentWhisper.id);
    }
    
    currentWhisper = whisper;
    
    // Update UI
    const header = document.getElementById('whisper-chat-header');
    const recipientEl = document.getElementById('whisper-chat-recipient');
    const expiryEl = document.getElementById('whisper-chat-expiry');
    const inputArea = document.getElementById('whisper-chat-input-area');
    
    if (!header || !recipientEl || !expiryEl || !inputArea) {
        console.error('Required DOM elements not found for whisper chat');
        alert('Failed to open whisper chat: UI elements not found');
        return;
    }
    
    const otherParticipant = whisper.sender_mask === currentSession.mask 
        ? whisper.recipient_mask 
        : whisper.sender_mask;
    
    recipientEl.textContent = otherParticipant;
    
    if (!whisper.expires_at) {
        console.warn('Whisper missing expires_at, using default');
        expiryEl.textContent = 'Expires in 24 hours';
    } else {
        const expiryDate = new Date(whisper.expires_at);
        const now = new Date();
        const hoursRemaining = (expiryDate - now) / (1000 * 60 * 60);
        if (hoursRemaining < 1) {
            expiryEl.innerHTML = `<span class="expiry-warning">Expires in ${Math.round(hoursRemaining * 60)} minutes</span>`;
        } else {
            expiryEl.textContent = `Expires in ${Math.round(hoursRemaining)} hours`;
        }
    }
    
    header.style.display = 'block';
    inputArea.style.display = 'block';
    
    // Highlight active whisper in list
    document.querySelectorAll('.whisper-item').forEach(el => {
        el.classList.remove('active');
    });
    const whisperEl = document.getElementById(`whisper-${whisper.id}`);
    if (whisperEl) {
        whisperEl.classList.add('active');
    }
    
    // Load whisper messages
    await loadWhisperMessages(whisper.id);
    
    // Subscribe to this whisper via WebSocket for real-time updates
    if (wsClient && currentRoom && whisperState === 'active') {
        wsClient.subscribe(currentRoom.id, whisper.id);
    }
}

// Load messages for a whisper
async function loadWhisperMessages(whisperId) {
    if (!currentRoom) return;
    
    try {
        const response = await fetch(`${API_BASE}/messages?room_id=${currentRoom.id}`);
        const data = await response.json();
        
        const messagesContainer = document.getElementById('whisper-chat-messages');
        messagesContainer.innerHTML = '';
        
        const whisperMessages = (data.items || []).filter(msg => 
            msg.type === 'whisper' && msg.whisper_id === whisperId
        );
        
        if (whisperMessages.length === 0) {
            messagesContainer.innerHTML = '<p class="empty">No messages yet. Start the conversation!</p>';
        } else {
            whisperMessages.forEach(msg => {
                const messageEl = createWhisperMessageElement(msg);
                messagesContainer.appendChild(messageEl);
            });
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    } catch (error) {
        console.error('Failed to load whisper messages:', error);
    }
}

// Create whisper message element
function createWhisperMessageElement(msg) {
    const messageEl = document.createElement('div');
    messageEl.className = 'message';
    messageEl.setAttribute('data-message-id', msg.id);
    messageEl.innerHTML = `
        <div class="message-header">
            <span class="sender-mask">${escapeHtml(msg.sender_mask)}</span>
            <span class="message-time">${formatDate(msg.created_at)}</span>
        </div>
        <div class="message-body">${escapeHtml(msg.body)}</div>
    `;
    return messageEl;
}

// Send whisper message
async function sendWhisperMessage() {
    if (!currentWhisper || !currentSession) {
        alert('No whisper selected');
        return;
    }
    
    const input = document.getElementById('whisper-message-input');
    const message = input.value.trim();
    
    if (!message) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/messages`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                room_id: currentRoom.id,
                sender_mask: currentSession.mask,
                type: 'whisper',
                body: message,
                whisper_id: currentWhisper.id,
            }),
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || 'Failed to send whisper');
        }
        
        input.value = '';
        await loadWhisperMessages(currentWhisper.id);
    } catch (error) {
        console.error('Failed to send whisper:', error);
        alert(error.message || 'Failed to send whisper. Please try again.');
    }
}

// Extend current whisper
async function extendCurrentWhisper() {
    if (!currentWhisper) {
        alert('No whisper selected');
        return;
    }
    
    const whisperId = currentWhisper.id;
    
    try {
        const response = await fetch(`${API_BASE}/whispers/${whisperId}/extend`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                hours: 24,
            }),
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || 'Failed to extend whisper');
        }
        
        // Reload whispers and find updated whisper
        await loadWhispers();
        const updatedWhisper = whispersList.find(w => w.id === whisperId);
        if (updatedWhisper) {
            currentWhisper = updatedWhisper;
            await openWhisperChat(updatedWhisper);
        }
    } catch (error) {
        console.error('Failed to extend whisper:', error);
        alert(error.message || 'Failed to extend whisper. Please try again.');
    }
}

// End current whisper
async function endCurrentWhisper() {
    if (!currentWhisper) {
        alert('No whisper selected');
        return;
    }
    
    if (!confirm('Are you sure you want to end this whisper?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/whispers/${currentWhisper.id}`, {
            method: 'DELETE',
        });
        
        if (!response.ok && response.status !== 204) {
            throw new Error('Failed to end whisper');
        }
        
            // Unsubscribe from whisper when closing
            if (currentWhisper && wsClient) {
                wsClient.unsubscribe(currentRoom.id, currentWhisper.id);
            }
        
        currentWhisper = null;
        document.getElementById('whisper-chat-header').style.display = 'none';
        document.getElementById('whisper-chat-input-area').style.display = 'none';
        document.getElementById('whisper-chat-messages').innerHTML = '<p class="empty">Select a whisper to view messages</p>';
        
        await loadWhispers();
    } catch (error) {
        console.error('Failed to end whisper:', error);
        alert('Failed to end whisper. Please try again.');
    }
}

// Handle Enter key in whisper input
document.addEventListener('DOMContentLoaded', () => {
    const whisperInput = document.getElementById('whisper-message-input');
    if (whisperInput) {
        whisperInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendWhisperMessage();
            }
        });
    }
});
