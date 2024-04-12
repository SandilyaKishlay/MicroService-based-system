import os
import psycopg2
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import secrets
import string

# Create Flask app
app = Flask(__name__)

# Configure app
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'your-secret-key'

# Database configuration
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5433')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'multi-service')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'QWEasd123')
conn = psycopg2.connect(
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    database=POSTGRES_DB
)
cur = conn.cursor()

# Define User model
class User:
    def __init__(self, username, email, password_hash, api_key):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.api_key = api_key

# Define function to initialize database
def init_db():
    # Create users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(256) NOT NULL,
            api_key VARCHAR(16) UNIQUE
        )
    """)
    conn.commit()

# Initialize database
init_db()

# Define middleware for API key verification
def require_api_key(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key is missing'}), 401

        cur.execute("SELECT * FROM users WHERE api_key = %s", (api_key,))
        user = cur.fetchone()
        if not user:
            return jsonify({'error': 'Invalid API key'}), 401
        user_id = user[0]  # Assuming user[0] contains the user ID
        request.user = user

        return func(*args, **kwargs)

    return decorated_function

# Define routes

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Validate input data
    if not username or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if user already exists
    cur.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
    existing_user = cur.fetchone()
    if existing_user:
        return jsonify({'error': 'Username or email already exists'}), 400

    # Generate API key
    api_key = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))

    # Hash password
    password_hash = generate_password_hash(password)

    # Insert new user into database
    cur.execute("INSERT INTO users (username, email, password_hash, api_key) VALUES (%s, %s, %s, %s)", (username, email, password_hash, api_key))
    conn.commit()

    return jsonify({'message': 'User registered successfully', 'api_key': api_key}), 201

@app.route('/api/user/<username>', methods=['GET'])
@require_api_key
def get_user_by_username(username):

    return jsonify({'username': request.user[1], 'email': request.user[2]}), 200

@app.route('/api/user/<username>', methods=['DELETE'])
@require_api_key
def delete_user(username):
    cur.execute("DELETE FROM users WHERE username = %s", (username,))
    conn.commit()
    return jsonify({'message': 'User deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
