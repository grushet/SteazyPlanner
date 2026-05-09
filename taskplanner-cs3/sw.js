self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    const target = new URL('./main_page.html', self.location.href).href;
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
            for (const client of clientList) {
                if (client.url === target && 'focus' in client) return client.focus();
            }
            return clients.openWindow(target);
        })
    );
});
