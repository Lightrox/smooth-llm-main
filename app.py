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

# Import SmoothLLM modules
import lib.perturbations as perturbations
import lib.defenses as defenses
import lib.attacks as attacks
from lib.attacks import CustomPromptAttack
import lib.language_models as language_models
import lib.model_configs as model_configs

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Database setup
DATABASE = 'smoothllm.db'

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

# Global variables for model
target_model = None
device = None

def load_model():
    """Load the target model for analysis."""
    global target_model, device
    
    if target_model is not None:
        return target_model
    
    try:
        # Use tinyllama as default model for web interface
        config = model_configs.MODELS['tinyllama']
        device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
        print(f"Using device: {device}")
        print(f"Loading model from: {config['model_path']}")
        
        target_model = language_models.LLM(
            model_path=config['model_path'],
            tokenizer_path=config['tokenizer_path'],
            conv_template_name=config['conversation_template'],
            device=device
        )
        
        print("Model loaded successfully!")
        return target_model
    except Exception as e:
        print(f"Error loading model: {e}")
        print("This might be due to missing model files or dependencies.")
        print("For testing purposes, the app will run with mock responses.")
        # Return a mock model for development
        return None

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

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
        
        # Load model
        model = load_model()
        if model is None:
            # Provide mock response for testing when model is not available
            print("Using mock response for testing...")
            
            # Simple heuristic to determine if prompt is potentially harmful
            harmful_keywords = [
                'kill', 'murder', 'harm', 'hurt', 'attack', 'destroy', 'poison', 
                'bomb', 'hack', 'steal', 'fraud', 'illegal', 'violence', 'weapon'
            ]
            
            prompt_lower = prompt.lower()
            is_harmful = any(keyword in prompt_lower for keyword in harmful_keywords)
            
            # Mock jailbreak percentage (higher for harmful prompts)
            jb_percentage = 75.0 if is_harmful else 15.0
            is_safe = jb_percentage < 50
            
            result = {
                'jb_percentage': jb_percentage,
                'is_safe': is_safe,
                'total_prompts': 1,
                'jailbroken_count': 1 if not is_safe else 0,
                'mock_response': True,
                'message': 'Using mock analysis (model not available)'
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
        
        # Create attack instance with user prompt
        attack = CustomPromptAttack(
            user_prompt=prompt,
            target_model=model
        )
        
        # Create defense instance
        defense = defenses.SmoothLLM(
            target_model=model,
            pert_type=pert_type,
            pert_pct=pert_pct,
            num_copies=num_copies
        )
        
        # Analyze the prompt
        jailbroken_results = []
        for i, prompt_obj in enumerate(attack.prompts[:1]):  # Only analyze first prompt
            defense.set_original_prompt(prompt_obj.perturbable_prompt)
            output = defense(prompt_obj)
            jb = defense.is_jailbroken(output)
            jailbroken_results.append(jb)
        
        # Calculate results
        jb_percentage = np.mean(jailbroken_results) * 100 if jailbroken_results else 0
        is_safe = jb_percentage < 50
        
        result = {
            'jb_percentage': jb_percentage,
            'is_safe': is_safe,
            'total_prompts': len(jailbroken_results),
            'jailbroken_count': sum(jailbroken_results)
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
def signin():
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
        print(f"Error in signin: {e}")
        return jsonify({'error': 'Sign in failed'}), 500

@app.route('/api/signup', methods=['POST'])
def signup():
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
        print(f"Error in signup: {e}")
        return jsonify({'error': 'Sign up failed'}), 500

@app.route('/api/signout', methods=['POST'])
def signout():
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

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Load model on startup
    print("Loading model...")
    load_model()
    print("Model loaded successfully!")
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
