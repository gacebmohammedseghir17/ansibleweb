from flask_socketio import SocketIO, emit
from functools import wraps
from datetime import datetime

socketio = SocketIO()

class NotificationManager:
    def __init__(self):
        self.connections = {}

    def emit_notification(self, user_id, message, notification_type='info', duration=5000):
        """Emit a notification to a specific user"""
        if user_id in self.connections:
            emit('notification', {
                'message': message,
                'type': notification_type,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            }, room=self.connections[user_id])

    def broadcast_notification(self, message, notification_type='info', duration=5000):
        """Broadcast a notification to all connected users"""
        emit('notification', {
            'message': message,
            'type': notification_type,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }, broadcast=True)

    def register_connection(self, user_id, sid):
        """Register a new WebSocket connection"""
        self.connections[user_id] = sid

    def remove_connection(self, user_id):
        """Remove a WebSocket connection"""
        if user_id in self.connections:
            del self.connections[user_id]

notification_manager = NotificationManager()

@socketio.on('connect')
def handle_connect():
    if not current_user.is_authenticated:
        return False
    notification_manager.register_connection(current_user.id, request.sid)
    emit('connected', {'status': 'success'})

@socketio.on('disconnect')
def handle_disconnect():
    if current_user.is_authenticated:
        notification_manager.remove_connection(current_user.id)

def notify_playbook_status(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if result.get('success'):
                notification_manager.emit_notification(
                    current_user.id,
                    f"Playbook execution completed successfully",
                    'success'
                )
            else:
                notification_manager.emit_notification(
                    current_user.id,
                    f"Playbook execution failed: {result.get('error', 'Unknown error')}",
                    'error'
                )
            return result
        except Exception as e:
            notification_manager.emit_notification(
                current_user.id,
                f"Error during playbook execution: {str(e)}",
                'error'
            )
            raise
    return wrapper