from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

login_manager = LoginManager()

class User(UserMixin):
    def __init__(self, id, username, password_hash, role):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role

    @staticmethod
    def get(user_id):
        # Only allow a single admin user
        users = {
            1: User(1, 'admin', generate_password_hash('admin'), 'admin')
        }
        return users.get(int(user_id))

    @staticmethod
    def get_by_username(username):
        # Only allow a single admin user
        users = {
            'admin': User(1, 'admin', generate_password_hash('admin'), 'admin')
        }
        return users.get(username)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                return {'error': 'Unauthorized'}, 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)