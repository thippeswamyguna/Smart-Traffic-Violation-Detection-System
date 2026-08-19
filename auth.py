import datetime
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
import jwt
from models import User

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]

        if not token:
            return jsonify({'message': 'Authorization token is missing!'}), 401

        try:
            secret = current_app.config['JWT_SECRET']
            data = jwt.decode(token, secret, algorithms=['HS256'])
            current_user = User.query.get(data['id'])
            if not current_user:
                return jsonify({'message': 'User associated with token not found!'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired! Please log in again.'}), 401
        except Exception as e:
            return jsonify({'message': 'Invalid token signature!'}), 401

        return f(current_user, *args, **kwargs)
    return decorated


def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            if current_user.role not in roles:
                return jsonify({'message': f'Forbidden! Requires one of roles: {roles}'}), 403
            return f(current_user, *args, **kwargs)
        return decorated
    return decorator


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required.'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid username or password.'}), 401

    secret = current_app.config['JWT_SECRET']
    payload = {
        'id': user.id,
        'username': user.username,
        'role': user.role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }

    token = jwt.encode(payload, secret, algorithm='HS256')

    return jsonify({
        'token': token,
        'user': user.to_dict(),
        'message': 'Login successful!'
    }), 200


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user_info(current_user):
    return jsonify({
        'user': current_user.to_dict()
    }), 200
