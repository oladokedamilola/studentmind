//frontend/js/chat-service.js
// Chat API Service
const ChatAPI = {
    // Get all conversations
    async getConversations() {
        try {
            const response = await fetch('/api/chat/conversations/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                if (response.status === 401) {
                    throw new Error('Not authenticated. Please login again.');
                }
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            // Ensure we always return an array
            return Array.isArray(data) ? data : [];
        } catch (error) {
            console.error('Error fetching conversations:', error);
            throw error;
        }
    },

    // Get single conversation with messages
    async getConversation(conversationId) {
        try {
            const response = await fetch(`/api/chat/conversations/${conversationId}/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error('Conversation not found');
                }
                if (response.status === 401) {
                    throw new Error('Not authenticated. Please login again.');
                }
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching conversation:', error);
            throw error;
        }
    },

    // Send a message
    async sendMessage(content, conversationId = null) {
        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
            
            console.log('Sending message:', { content, conversationId });
            
            const response = await fetch('/api/chat/send/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    content: content,
                    conversation_id: conversationId
                }),
                credentials: 'same-origin'
            });
            
            console.log('Response status:', response.status);
            
            const data = await response.json();
            console.log('Response data:', data);
            
            if (!response.ok) {
                if (response.status === 401) {
                    throw new Error('Your session has expired. Please login again.');
                } else if (response.status === 403) {
                    throw new Error('You don\'t have permission to perform this action.');
                } else if (response.status === 429) {
                    throw new Error('Too many requests. Please wait a moment.');
                } else {
                    throw new Error(data.error || data.message || 'Failed to send message');
                }
            }
            
            return data;
        } catch (error) {
            console.error('Error sending message:', error);
            throw error;
        }
    },

    // Regenerate AI response for a user message
    async regenerateResponse(messageId) {
        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
            
            console.log('Regenerating response for message:', messageId);
            
            const response = await fetch('/api/chat/regenerate/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ message_id: messageId }),
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to regenerate response');
            }
            
            return data;
        } catch (error) {
            console.error('Error regenerating response:', error);
            throw error;
        }
    },

    // Edit a message and resend
    async editAndResend(messageId, newContent) {
        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
            
            console.log('Editing message:', { messageId, newContent });
            
            const response = await fetch('/api/chat/edit-resend/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ 
                    message_id: messageId,
                    content: newContent
                }),
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to edit message');
            }
            
            return data;
        } catch (error) {
            console.error('Error editing message:', error);
            throw error;
        }
    },

    // Stop the current AI response generation
    async stopGeneration(conversationId) {
        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
            
            console.log('Stopping generation for conversation:', conversationId);
            
            const response = await fetch('/api/chat/stop-generation/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ conversation_id: conversationId }),
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to stop generation');
            }
            
            return data;
        } catch (error) {
            console.error('Error stopping generation:', error);
            throw error;
        }
    },

    // Close conversation
    async closeConversation(conversationId) {
        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
            
            const response = await fetch(`/api/chat/conversations/${conversationId}/close/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to close conversation');
            }
            
            return data;
        } catch (error) {
            console.error('Error closing conversation:', error);
            throw error;
        }
    },

    // Mark messages as read
    async markAsRead(conversationId) {
        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
            
            const response = await fetch(`/api/chat/conversations/${conversationId}/mark-read/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to mark messages as read');
            }
            
            return data;
        } catch (error) {
            console.error('Error marking messages as read:', error);
            throw error;
        }
    }
};