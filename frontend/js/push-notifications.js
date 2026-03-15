// Check if push notifications are supported
function isPushSupported() {
    return 'serviceWorker' in navigator && 'PushManager' in window;
}

// Request permission
async function requestNotificationPermission() {
    if (!isPushSupported()) {
        console.log('Push notifications not supported');
        return false;
    }
    
    try {
        const permission = await Notification.requestPermission();
        return permission === 'granted';
    } catch (error) {
        console.log('Error requesting permission:', error);
        return false;
    }
}

// Subscribe to push notifications
async function subscribeToPush() {
    if (!isPushSupported()) return;
    
    try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array('YOUR_VAPID_PUBLIC_KEY')
        });
        
        // Send subscription to server
        await fetch('/api/notifications/subscribe/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(subscription)
        });
        
        console.log('Push subscription successful');
    } catch (error) {
        console.log('Push subscription failed:', error);
    }
}

// Helper to convert VAPID key
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');
    
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

// Show notification
function showLocalNotification(title, body, icon = '/static/icons/icon-192x192.png') {
    if (Notification.permission === 'granted') {
        navigator.serviceWorker.ready.then(registration => {
            registration.showNotification(title, {
                body: body,
                icon: icon,
                badge: '/static/icons/badge-72x72.png',
                vibrate: [200, 100, 200],
                actions: [
                    { action: 'open', title: 'Open App' },
                    { action: 'dismiss', title: 'Dismiss' }
                ]
            });
        });
    }
}