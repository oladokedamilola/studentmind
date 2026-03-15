// IndexedDB for offline message storage
const DB_NAME = 'mindhaven-offline';
const DB_VERSION = 1;
const STORE_NAME = 'messages';

let db;

// Open database
function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => {
            db = request.result;
            resolve(db);
        };
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains(STORE_NAME)) {
                const store = db.createObjectStore(STORE_NAME, { keyPath: 'id', autoIncrement: true });
                store.createIndex('timestamp', 'timestamp', { unique: false });
                store.createIndex('synced', 'synced', { unique: false });
            }
        };
    });
}

// Save message offline
async function saveMessageOffline(messageData) {
    const db = await openDB();
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    
    return new Promise((resolve, reject) => {
        const request = store.add({
            ...messageData,
            timestamp: new Date().toISOString(),
            synced: false
        });
        
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

// Get unsynced messages
async function getUnsyncedMessages() {
    const db = await openDB();
    const tx = db.transaction(STORE_NAME, 'readonly');
    const store = tx.objectStore(STORE_NAME);
    const index = store.index('synced');
    
    return new Promise((resolve, reject) => {
        const request = index.getAll(false);
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

// Mark message as synced
async function markMessageSynced(id) {
    const db = await openDB();
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    
    return new Promise((resolve, reject) => {
        const getRequest = store.get(id);
        
        getRequest.onsuccess = () => {
            const message = getRequest.result;
            message.synced = true;
            const updateRequest = store.put(message);
            updateRequest.onsuccess = () => resolve();
            updateRequest.onerror = () => reject(updateRequest.error);
        };
        
        getRequest.onerror = () => reject(getRequest.error);
    });
}

// Sync offline messages when online
async function syncOfflineMessages() {
    if (!navigator.onLine) return;
    
    const messages = await getUnsyncedMessages();
    
    for (const message of messages) {
        try {
            const response = await fetch('/api/chat/send/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify(message.data)
            });
            
            if (response.ok) {
                await markMessageSynced(message.id);
            }
        } catch (error) {
            console.log('Failed to sync message:', message.id);
        }
    }
}

// Listen for online/offline events
window.addEventListener('online', () => {
    syncOfflineMessages();
    showOfflineIndicator(false);
});

window.addEventListener('offline', () => {
    showOfflineIndicator(true);
});

// Show/hide offline indicator
function showOfflineIndicator(isOffline) {
    let indicator = document.getElementById('offline-indicator');
    
    if (isOffline) {
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'offline-indicator';
            indicator.className = 'offline-indicator';
            indicator.innerHTML = `
                <div class="alert alert-warning mb-0 rounded-0">
                    <div class="container">
                        <span>📴 You're offline. Messages will be sent when connection returns.</span>
                    </div>
                </div>
            `;
            document.body.prepend(indicator);
        }
    } else {
        if (indicator) {
            indicator.remove();
            // Show success toast
            showToast('Back online! Messages synced.', 'success');
        }
    }
}