// Notification System
class NotificationSystem {
    constructor() {
        this.container = document.querySelector('.toast-container') || this.createContainer();
    }

    createContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
        return container;
    }

    show(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="toast-header">
                <i class="fas fa-${this.getIcon(type)} me-2"></i>
                <strong class="me-auto">${this.getTitle(type)}</strong>
                <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
            <div class="toast-body">${message}</div>
        `;

        this.container.appendChild(toast);
        setTimeout(() => toast.classList.add('show'), 100);

        if (duration > 0) {
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }

        return toast;
    }

    getIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || icons.info;
    }

    getTitle(type) {
        const titles = {
            success: 'Success',
            error: 'Error',
            warning: 'Warning',
            info: 'Information'
        };
        return titles[type] || titles.info;
    }

    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }
}

// Initialize notification system
const notifications = new NotificationSystem();

// WebSocket connection for real-time notifications
class NotificationWebSocket {
    constructor() {
        this.connect();
    }

    connect() {
        this.ws = new WebSocket(`ws://${window.location.host}/ws/notifications`);
        this.ws.onmessage = this.handleMessage.bind(this);
        this.ws.onclose = () => setTimeout(() => this.connect(), 5000);
    }

    handleMessage(event) {
        const data = JSON.parse(event.data);
        notifications[data.type](data.message, data.duration);
    }
}

// Initialize WebSocket connection when document is ready
document.addEventListener('DOMContentLoaded', () => {
    new NotificationWebSocket();
});