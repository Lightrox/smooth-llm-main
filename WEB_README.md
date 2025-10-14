# SmoothLLM Web Interface

A modern web interface for the SmoothLLM AI safety defense system. This interface allows users to test prompts for safety using the SmoothLLM defense mechanism.

## Features

- 🎨 **Modern UI**: Beautiful, responsive design with gradient backgrounds and smooth animations
- 🔐 **User Authentication**: Sign up and sign in functionality with secure password hashing
- 📝 **Prompt Analysis**: Test any prompt for safety using configurable perturbation parameters
- 📊 **Real-time Results**: Get instant feedback on whether a prompt is safe or unsafe
- 📚 **Prompt History**: View and manage your analysis history (requires sign in)
- ⚙️ **Configurable Parameters**: Adjust number of perturbations, perturbation type, and percentage
- 📱 **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Web Interface

```bash
python run_web.py
```

Or directly:

```bash
python app.py
```

### 3. Access the Interface

Open your browser and navigate to: `http://localhost:5000`

## Usage

### Basic Analysis

1. **Enter a Prompt**: Type or paste the prompt you want to analyze in the text area
2. **Configure Parameters**:
   - **Number of Perturbations**: Choose how many copies to create (5-25)
   - **Perturbation Type**: Select the type of perturbation to apply
   - **Perturbation Percentage**: Adjust the percentage of tokens to perturb (5-20%)
3. **Click "Analyze Safety"**: The system will process your prompt and show results

### User Account Features

1. **Sign Up**: Create a new account to access additional features
2. **Sign In**: Access your account and prompt history
3. **View History**: See all your previous prompt analyses
4. **Persistent Storage**: Your analysis history is saved and accessible across sessions

## API Endpoints

The web interface provides several REST API endpoints:

- `POST /api/analyze` - Analyze a prompt for safety
- `POST /api/signin` - User sign in
- `POST /api/signup` - User sign up
- `POST /api/signout` - User sign out
- `GET /api/history` - Get user's prompt history
- `GET /api/user` - Get current user information

## Configuration

### Model Configuration

The system uses models defined in `lib/model_configs.py`. By default, it uses the `tinyllama` model for the web interface. You can modify the model configuration to use different models:

```python
MODELS = {
    'tinyllama': {
        'model_path': 'TinyLlama/TinyLlama-1.1B-Chat-v1.0',
        'tokenizer_path': 'TinyLlama/TinyLlama-1.1B-Chat-v1.0',
        'conversation_template': 'llama-2'
    },
    # Add other models as needed
}
```

### Database

The application uses SQLite for storing user accounts and prompt history. The database file (`smoothllm.db`) is created automatically on first run.

## File Structure

```
├── app.py                 # Flask application and API endpoints
├── run_web.py            # Web interface startup script
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css     # CSS styles
│   └── js/
│       └── script.js     # JavaScript functionality
└── lib/                  # SmoothLLM core library
    ├── attacks.py
    ├── defenses.py
    ├── language_models.py
    ├── model_configs.py
    └── perturbations.py
```

## Security Features

- **Password Hashing**: User passwords are hashed using SHA-256
- **Session Management**: Secure session handling for user authentication
- **Input Validation**: All user inputs are validated and sanitized
- **SQL Injection Protection**: Using parameterized queries

## Browser Compatibility

The web interface is compatible with all modern browsers:
- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Troubleshooting

### Common Issues

1. **Model Loading Errors**: Ensure you have the required model files and dependencies installed
2. **Database Errors**: Check file permissions for the SQLite database
3. **Port Already in Use**: Change the port in `app.py` if port 5000 is occupied

### Debug Mode

Run with debug mode enabled for detailed error messages:

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the SmoothLLM research paper: "SmoothLLM: Defending Large Language Models Against Jailbreaking Attacks"
- Uses Flask for the web framework
- Icons from Font Awesome
- Fonts from Google Fonts
