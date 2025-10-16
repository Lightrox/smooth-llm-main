from flask import Flask, render_template, request, jsonify, session
import os
import torch
import numpy as np
import pandas as pd
import json
import sqlite3
from datetime import datetime
import hashlib
import secrets

# Import SmoothLLM modules (disabled for Netlify deployment)
# import lib.perturbations as perturbations
# import lib.defenses as defenses
# import lib.attacks as attacks
# from lib.attacks import CustomPromptAttack
# import lib.language_models as language_models
# import lib.model_configs as model_configs

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Database setup
DATABASE = os.path.join(os.path.dirname(__file__), 'smoothllm.db')

def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Prompt history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prompt_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            prompt TEXT NOT NULL,
            is_safe BOOLEAN NOT NULL,
            jailbreak_rate REAL NOT NULL,
            perturbations INTEGER NOT NULL,
            perturbation_type TEXT NOT NULL,
            perturbation_pct INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify password against hash."""
    return hash_password(password) == password_hash

# Model loading disabled for Netlify deployment
# Using mock analysis instead

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/signin')
def signin():
    """Render the sign-in page."""
    return render_template('signin.html')

@app.route('/signup')
def signup():
    """Render the sign-up page."""
    return render_template('signup.html')

@app.route('/profile')
def profile():
    """Render the profile page. Client will fetch user via /api/user and redirect if unauthenticated."""
    return render_template('profile.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_prompt():
    """Analyze a prompt using SmoothLLM."""
    try:
        data = request.get_json()
        
        # Extract parameters
        prompt = data.get('prompt', '').strip()
        num_copies = data.get('smoothllm_num_copies', 10)
        pert_type = data.get('smoothllm_pert_type', 'RandomPatchPerturbation')
        pert_pct = data.get('smoothllm_pert_pct', 10)
        target_model_name = data.get('target_model', 'tinyllama')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Use mock analysis for Netlify deployment
        print("Using mock analysis for Netlify deployment...")
        
        # Simple heuristic to determine if prompt is potentially harmful
        harmful_keywords = [
            'kill', 'murder', 'harm', 'hurt', 'attack', 'destroy', 'poison', 
            'bomb', 'hack', 'steal', 'fraud', 'illegal', 'violence', 'weapon',
            'hate', 'discrimination', 'suicide', 'self-harm', 'dangerous',
            'bomb', 'terrorist', 'threat', 'danger', 'weapon', 'gun'
        ]
        
        prompt_lower = prompt.lower()
        is_harmful = any(keyword in prompt_lower for keyword in harmful_keywords)
        
        # Mock jailbreak percentage (higher for harmful prompts)
        jb_percentage = 75.0 if is_harmful else 15.0
        is_safe = bool(jb_percentage < 50)
        
        result = {
            'jb_percentage': float(jb_percentage),
            'is_safe': is_safe,
            'total_prompts': 1,
            'jailbroken_count': int(1 if not is_safe else 0),
            'mock_response': True,
            'message': 'Using mock analysis (Netlify deployment - no ML models)'
        }
        
        # Save to history if user is logged in
        if 'user_id' in session:
            save_prompt_history(
                user_id=session['user_id'],
                prompt=prompt,
                is_safe=is_safe,
                jailbreak_rate=jb_percentage,
                perturbations=num_copies,
                perturbation_type=pert_type,
                perturbation_pct=pert_pct
            )
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in analyze_prompt: {e}")
        return jsonify({'error': 'Analysis failed'}), 500

@app.route('/api/signin', methods=['POST'])
def api_signin():
    """Handle user sign in."""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE email = ?', (email,)
        ).fetchone()
        conn.close()
        
        if user and verify_password(password, user['password_hash']):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user['id'],
                    'name': user['name'],
                    'email': user['email']
                }
            })
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
            
    except Exception as e:
        print(f"Error in api_signin: {e}")
        return jsonify({'error': 'Sign in failed'}), 500

@app.route('/api/signup', methods=['POST'])
def api_signup():
    """Handle user sign up."""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not all([name, email, password]):
            return jsonify({'error': 'All fields are required'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        conn = get_db_connection()
        
        # Check if user already exists
        existing_user = conn.execute(
            'SELECT id FROM users WHERE email = ?', (email,)
        ).fetchone()
        
        if existing_user:
            conn.close()
            return jsonify({'error': 'User already exists'}), 409
        
        # Create new user
        password_hash = hash_password(password)
        cursor = conn.execute(
            'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
            (name, email, password_hash)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Set session
        session['user_id'] = user_id
        session['user_name'] = name
        session['user_email'] = email
        
        return jsonify({
            'success': True,
            'user': {
                'id': user_id,
                'name': name,
                'email': email
            }
        })
        
    except Exception as e:
        print(f"Error in api_signup: {e}")
        return jsonify({'error': 'Sign up failed'}), 500

@app.route('/api/signout', methods=['POST'])
def api_signout():
    """Handle user sign out."""
    session.clear()
    return jsonify({'success': True})

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get user's prompt history."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        conn = get_db_connection()
        history = conn.execute(
            '''SELECT * FROM prompt_history 
               WHERE user_id = ? 
               ORDER BY created_at DESC 
               LIMIT 50''',
            (session['user_id'],)
        ).fetchall()
        conn.close()
        
        history_list = []
        for item in history:
            history_list.append({
                'id': item['id'],
                'prompt': item['prompt'],
                'is_safe': bool(item['is_safe']),
                'jailbreak_rate': item['jailbreak_rate'],
                'perturbations': item['perturbations'],
                'perturbation_type': item['perturbation_type'],
                'perturbation_pct': item['perturbation_pct'],
                'created_at': item['created_at']
            })
        
        return jsonify({'history': history_list})
        
    except Exception as e:
        print(f"Error in get_history: {e}")
        return jsonify({'error': 'Failed to fetch history'}), 500

def save_prompt_history(user_id, prompt, is_safe, jailbreak_rate, perturbations, perturbation_type, perturbation_pct):
    """Save prompt analysis to history."""
    try:
        conn = get_db_connection()
        conn.execute(
            '''INSERT INTO prompt_history 
               (user_id, prompt, is_safe, jailbreak_rate, perturbations, perturbation_type, perturbation_pct)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (user_id, prompt, is_safe, jailbreak_rate, perturbations, perturbation_type, perturbation_pct)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving prompt history: {e}")

@app.route('/api/user', methods=['GET'])
def get_user():
    """Get current user information."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return jsonify({
        'user': {
            'id': session['user_id'],
            'name': session['user_name'],
            'email': session['user_email']
        }
    })

@app.route('/api/user/stats', methods=['GET'])
def get_user_stats():
    """Get user statistics."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        conn = get_db_connection()
        
        # Get total analyses count
        total_analyses = conn.execute(
            'SELECT COUNT(*) as count FROM prompt_history WHERE user_id = ?',
            (session['user_id'],)
        ).fetchone()['count']
        
        # Get safe/unsafe counts
        safe_count = conn.execute(
            'SELECT COUNT(*) as count FROM prompt_history WHERE user_id = ? AND is_safe = 1',
            (session['user_id'],)
        ).fetchone()['count']
        
        unsafe_count = total_analyses - safe_count
        
        # Get average jailbreak rate
        avg_jailbreak = conn.execute(
            'SELECT AVG(jailbreak_rate) as avg_rate FROM prompt_history WHERE user_id = ?',
            (session['user_id'],)
        ).fetchone()['avg_rate'] or 0
        
        conn.close()
        
        return jsonify({
            'total_analyses': total_analyses,
            'safe_prompts': safe_count,
            'unsafe_prompts': unsafe_count,
            'avg_jailbreak_rate': round(avg_jailbreak, 1)
        })
        
    except Exception as e:
        print(f"Error in get_user_stats: {e}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500

@app.route('/api/user/export', methods=['GET'])
def export_user_data():
    """Export user data as JSON."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        conn = get_db_connection()
        
        # Get user info
        user = conn.execute(
            'SELECT * FROM users WHERE id = ?', (session['user_id'],)
        ).fetchone()
        
        # Get user history
        history = conn.execute(
            '''SELECT * FROM prompt_history 
               WHERE user_id = ? 
               ORDER BY created_at DESC''',
            (session['user_id'],)
        ).fetchall()
        
        conn.close()
        
        # Prepare export data
        export_data = {
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'created_at': user['created_at']
            },
            'history': [
                {
                    'id': item['id'],
                    'prompt': item['prompt'],
                    'is_safe': bool(item['is_safe']),
                    'jailbreak_rate': item['jailbreak_rate'],
                    'perturbations': item['perturbations'],
                    'perturbation_type': item['perturbation_type'],
                    'perturbation_pct': item['perturbation_pct'],
                    'created_at': item['created_at']
                }
                for item in history
            ],
            'export_date': datetime.now().isoformat(),
            'total_records': len(history)
        }
        
        return jsonify(export_data)
        
    except Exception as e:
        print(f"Error in export_user_data: {e}")
        return jsonify({'error': 'Failed to export data'}), 500

# Initialize database
init_db()

if __name__ == '__main__':
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
