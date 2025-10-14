// Authentication JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is already logged in
    checkAuthStatus();
    
    // Set up form handlers
    setupFormHandlers();
});

function checkAuthStatus() {
    // Check if user is already logged in
    fetch('/api/user')
    .then(response => response.json())
    .then(data => {
        if (data.user) {
            // User is already logged in, redirect to home
            window.location.href = '/';
        }
    })
    .catch(error => {
        // User is not logged in, stay on auth page
        console.log('User not authenticated');
    });
}

function setupFormHandlers() {
    // Sign in form
    const signInForm = document.getElementById('signInForm');
    if (signInForm) {
        signInForm.addEventListener('submit', handleSignIn);
    }
    
    // Sign up form
    const signUpForm = document.getElementById('signUpForm');
    if (signUpForm) {
        signUpForm.addEventListener('submit', handleSignUp);
    }
    
    // Password confirmation validation
    const confirmPassword = document.getElementById('confirmPassword');
    if (confirmPassword) {
        confirmPassword.addEventListener('input', validatePasswordMatch);
    }
}

function handleSignIn(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const email = formData.get('email').trim();
    const password = formData.get('password');
    
    if (!email || !password) {
        showMessage('Please fill in all fields', 'error');
        return;
    }
    
    showLoading(true);
    
    fetch('/api/signin', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        
        if (data.success) {
            showMessage('Successfully signed in! Redirecting...', 'success');
            
            // Store user data in localStorage
            localStorage.setItem('currentUser', JSON.stringify(data.user));
            
            // Redirect to home page after a short delay
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        } else {
            showMessage(data.error || 'Sign in failed', 'error');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        showMessage('An error occurred during sign in', 'error');
    });
}

function handleSignUp(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const name = formData.get('name').trim();
    const email = formData.get('email').trim();
    const password = formData.get('password');
    const confirmPassword = formData.get('confirmPassword');
    
    if (!name || !email || !password || !confirmPassword) {
        showMessage('Please fill in all fields', 'error');
        return;
    }
    
    if (password !== confirmPassword) {
        showMessage('Passwords do not match', 'error');
        return;
    }
    
    if (password.length < 6) {
        showMessage('Password must be at least 6 characters long', 'error');
        return;
    }
    
    if (!document.getElementById('agreeTerms').checked) {
        showMessage('Please agree to the terms and conditions', 'error');
        return;
    }
    
    showLoading(true);
    
    fetch('/api/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, password })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        
        if (data.success) {
            showMessage('Account created successfully! Redirecting...', 'success');
            
            // Store user data in localStorage
            localStorage.setItem('currentUser', JSON.stringify(data.user));
            
            // Redirect to home page after a short delay
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        } else {
            showMessage(data.error || 'Sign up failed', 'error');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        showMessage('An error occurred during sign up', 'error');
    });
}

function validatePasswordMatch() {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    if (confirmPassword && password !== confirmPassword) {
        document.getElementById('confirmPassword').setCustomValidity('Passwords do not match');
    } else {
        document.getElementById('confirmPassword').setCustomValidity('');
    }
}

function showMessage(message, type) {
    const messageContainer = document.getElementById('messageContainer');
    const messageContent = document.getElementById('messageContent');
    
    if (!messageContainer || !messageContent) return;
    
    // Clear previous messages
    messageContent.innerHTML = '';
    
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    
    const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
    messageDiv.innerHTML = `
        <i class="fas ${icon}"></i>
        <span>${message}</span>
    `;
    
    messageContent.appendChild(messageDiv);
    messageContainer.style.display = 'block';
    
    // Auto-hide after 5 seconds for success messages
    if (type === 'success') {
        setTimeout(() => {
            messageContainer.style.display = 'none';
        }, 5000);
    }
}

function showLoading(show) {
    const loadingSpinner = document.getElementById('loadingSpinner');
    const signInBtn = document.getElementById('signInBtn');
    const signUpBtn = document.getElementById('signUpBtn');
    
    if (loadingSpinner) {
        loadingSpinner.style.display = show ? 'block' : 'none';
    }
    
    if (signInBtn) {
        signInBtn.disabled = show;
        signInBtn.innerHTML = show ? 
            '<i class="fas fa-spinner fa-spin"></i> Signing in...' : 
            '<i class="fas fa-sign-in-alt"></i> Sign In';
    }
    
    if (signUpBtn) {
        signUpBtn.disabled = show;
        signUpBtn.innerHTML = show ? 
            '<i class="fas fa-spinner fa-spin"></i> Creating account...' : 
            '<i class="fas fa-user-plus"></i> Create Account';
    }
}

function hideLoading() {
    showLoading(false);
}
