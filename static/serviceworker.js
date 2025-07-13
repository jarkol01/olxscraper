// Service Worker for OLX Scraper Push Notifications

self.addEventListener('push', function(event) {
    console.log('Push event received:', event);

    let data = {};
    if (event.data) {
        try {
            data = event.data.json();
        } catch (e) {
            data = {
                head: 'New Notification',
                body: event.data.text() || 'You have a new notification',
                url: '/'
            };
        }
    }

    const title = data.head || 'OLX Scraper';
    const options = {
        body: data.body || 'New search results available!',
        icon: '/static/icon-192x192.png',
        badge: '/static/badge-72x72.png',
        data: {
            url: data.url || '/'
        },
        actions: [
            {
                action: 'view',
                title: 'View Results'
            },
            {
                action: 'dismiss',
                title: 'Dismiss'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

self.addEventListener('notificationclick', function(event) {
    console.log('Notification click received:', event);

    event.notification.close();

    if (event.action === 'dismiss') {
        return;
    }

    // Default action or 'view' action
    const urlToOpen = event.notification.data.url || '/';

    event.waitUntil(
        clients.matchAll({
            type: 'window',
            includeUncontrolled: true
        }).then(function(clientList) {
            // Check if there's already a window/tab open with the target URL
            for (let client of clientList) {
                if (client.url === urlToOpen && 'focus' in client) {
                    return client.focus();
                }
            }

            // If no window/tab is open, open a new one
            if (clients.openWindow) {
                return clients.openWindow(urlToOpen);
            }
        })
    );
});

self.addEventListener('pushsubscriptionchange', function(event) {
    console.log('Push subscription change event:', event);

    event.waitUntil(
        fetch('/webpush/save_information/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                subscription: event.newSubscription
            })
        })
    );
});

// Handle service worker installation
self.addEventListener('install', function(event) {
    console.log('Service worker installing...');
    self.skipWaiting();
});

// Handle service worker activation
self.addEventListener('activate', function(event) {
    console.log('Service worker activating...');
    event.waitUntil(self.clients.claim());
});
