// Global variables
let currentUser = null;
let promptHistory = [];

// DOM elements
const smoothllmForm = document.getElementById('smoothllmForm');
const submitBtn = document.getElementById('submitBtn');
const resultsSection = document.getElementById('resultsSection');
const loadingSpinner = document.getElementById('loadingSpinner');
const signInBtn = document.getElementById('signInBtn');
const signInModal = document.getElementById('signInModal');
const signUpModal = document.getElementById('signUpModal');
const historyModal = document.getElementById('historyModal');
const perturbationPct = document.getElementById('perturbationPct');
const perturbationValue = document.getElementById('perturbationValue');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadUserSession();
});

function initializeApp() {
    // Update perturbation percentage display
    updatePerturbationDisplay();
    
    // Check if user is logged in
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        updateUIForLoggedInUser();
    }
}

function setupEventListeners() {
    // Form submission
    smoothllmForm.addEventListener('submit', handleFormSubmit);
    
    // Perturbation range slider
    perturbationPct.addEventListener('input', updatePerturbationDisplay);
    
    // Modal controls
    signInBtn.addEventListener('click', () => openModal('signInModal'));
    
    // Close modals when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            closeModal(event.target.id);
        }
    });
    
    // Close buttons
    document.querySelectorAll('.close').forEach(closeBtn => {
        closeBtn.addEventListener('click', function() {
            const modal = this.closest('.modal');
            closeModal(modal.id);
        });
    });
    
    // Sign in form
    document.getElementById('signInForm').addEventListener('submit', handleSignIn);
    
    // Sign up form
    document.getElementById('signUpForm').addEventListener('submit', handleSignUp);
    
    // Modal navigation
    document.getElementById('signUpLink').addEventListener('click', function(e) {
        e.preventDefault();
        closeModal('signInModal');
        openModal('signUpModal');
    });
    
    document.getElementById('signInLink').addEventListener('click', function(e) {
        e.preventDefault();
        closeModal('signUpModal');
        openModal('signInModal');
    });
}

function updatePerturbationDisplay() {
    perturbationValue.textContent = perturbationPct.value + '%';
}

function handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(smoothllmForm);
    const prompt = formData.get('prompt').trim();
    const perturbations = formData.get('perturbations');
    const perturbationType = formData.get('perturbationType');
    const perturbationPct = formData.get('perturbationPct');
    
    if (!prompt) {
        alert('Please enter a prompt to analyze.');
        return;
    }
    
    // Show loading spinner
    showLoading();
    
    // Prepare request data
    const requestData = {
        prompt: prompt,
        smoothllm_num_copies: parseInt(perturbations),
        smoothllm_pert_type: perturbationType,
        smoothllm_pert_pct: parseInt(perturbationPct),
        target_model: 'tinyllama' // Default model
    };
    
    // Make API call
    fetch('/api/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        displayResults(data, requestData);
        
        // Save to history if user is logged in
        if (currentUser) {
            saveToHistory(prompt, data, requestData);
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        alert('An error occurred while analyzing the prompt. Please try again.');
    });
}

function showLoading() {
    loadingSpinner.style.display = 'block';
    resultsSection.style.display = 'none';
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
}

function hideLoading() {
    loadingSpinner.style.display = 'none';
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<i class="fas fa-shield-check"></i> Analyze Safety';
}

function displayResults(data, requestData) {
    const resultStatus = document.getElementById('resultStatus');
    const jailbreakRate = document.getElementById('jailbreakRate');
    const perturbationsUsed = document.getElementById('perturbationsUsed');
    const perturbationTypeUsed = document.getElementById('perturbationTypeUsed');
    
    // Determine if the prompt is safe or unsafe
    const isSafe = data.jb_percentage < 50; // Less than 50% jailbreak rate is considered safe
    
    // Update status display
    resultStatus.textContent = isSafe ? 'SAFE' : 'UNSAFE';
    resultStatus.className = `result-status ${isSafe ? 'safe' : 'unsafe'}`;
    
    // Update result details
    jailbreakRate.textContent = `${data.jb_percentage.toFixed(2)}%`;
    perturbationsUsed.textContent = requestData.smoothllm_num_copies;
    perturbationTypeUsed.textContent = requestData.smoothllm_pert_type.replace('Perturbation', '');
    
    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function saveToHistory(prompt, result, requestData) {
    const historyItem = {
        id: Date.now(),
        prompt: prompt,
        timestamp: new Date().toISOString(),
        isSafe: result.jb_percentage < 50,
        jailbreakRate: result.jb_percentage,
        perturbations: requestData.smoothllm_num_copies,
        perturbationType: requestData.smoothllm_pert_type,
        perturbationPct: requestData.smoothllm_pert_pct
    };
    
    promptHistory.unshift(historyItem);
    
    // Keep only last 50 items
    if (promptHistory.length > 50) {
        promptHistory = promptHistory.slice(0, 50);
    }
    
    // Save to localStorage
    localStorage.setItem(`promptHistory_${currentUser.id}`, JSON.stringify(promptHistory));
}

function loadUserSession() {
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        loadPromptHistory();
        updateUIForLoggedInUser();
    }
}

function loadPromptHistory() {
    if (currentUser) {
        // Try to load from server first
        fetch('/api/history')
        .then(response => response.json())
        .then(data => {
            if (data.history) {
                promptHistory = data.history;
            }
        })
        .catch(error => {
            console.error('Error loading history from server:', error);
            // Fallback to localStorage
            const savedHistory = localStorage.getItem(`promptHistory_${currentUser.id}`);
            if (savedHistory) {
                promptHistory = JSON.parse(savedHistory);
            }
        });
    }
}

function updateUIForLoggedInUser() {
    if (currentUser) {
        signInBtn.innerHTML = `<i class="fas fa-user"></i> ${currentUser.name}`;
        signInBtn.onclick = () => openModal('historyModal');
        
        // Add history button to navbar
        if (!document.getElementById('historyBtn')) {
            const historyBtn = document.createElement('button');
            historyBtn.id = 'historyBtn';
            historyBtn.className = 'btn-signin';
            historyBtn.innerHTML = '<i class="fas fa-history"></i> History';
            historyBtn.style.marginRight = '1rem';
            historyBtn.onclick = () => openModal('historyModal');
            
            const navActions = document.querySelector('.nav-actions');
            navActions.insertBefore(historyBtn, signInBtn);
        }
    }
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
    
    if (modalId === 'historyModal') {
        displayPromptHistory();
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

function displayPromptHistory() {
    const historyContent = document.getElementById('historyContent');
    
    if (promptHistory.length === 0) {
        historyContent.innerHTML = '<p style="text-align: center; color: #6b7280; padding: 2rem;">No prompt history found.</p>';
        return;
    }
    
    historyContent.innerHTML = promptHistory.map(item => `
        <div class="history-item">
            <div class="history-prompt">${item.prompt}</div>
            <div class="history-meta">
                <span>${new Date(item.timestamp).toLocaleString()}</span>
                <span class="history-status ${item.isSafe ? 'safe' : 'unsafe'}">
                    ${item.isSafe ? 'Safe' : 'Unsafe'}
                </span>
            </div>
        </div>
    `).join('');
}

function handleSignIn(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const email = formData.get('email');
    const password = formData.get('password');
    
    if (!email || !password) {
        alert('Please enter both email and password.');
        return;
    }
    
    // Make API call to backend
    fetch('/api/signin', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentUser = data.user;
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            loadPromptHistory();
            updateUIForLoggedInUser();
            closeModal('signInModal');
            e.target.reset();
            alert('Successfully signed in!');
        } else {
            alert(data.error || 'Sign in failed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred during sign in');
    });
}

function handleSignUp(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const name = formData.get('name');
    const email = formData.get('email');
    const password = formData.get('password');
    
    if (!name || !email || !password) {
        alert('Please fill in all fields.');
        return;
    }
    
    if (password.length < 6) {
        alert('Password must be at least 6 characters long.');
        return;
    }
    
    // Make API call to backend
    fetch('/api/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentUser = data.user;
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            loadPromptHistory();
            updateUIForLoggedInUser();
            closeModal('signUpModal');
            e.target.reset();
            alert('Successfully signed up!');
        } else {
            alert(data.error || 'Sign up failed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred during sign up');
    });
}

// Utility function to format perturbation type names
function formatPerturbationType(type) {
    return type.replace('Perturbation', '').replace(/([A-Z])/g, ' $1').trim();
}

// Add smooth scrolling for better UX
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Escape key to close modals
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal[style*="block"]');
        if (openModal) {
            closeModal(openModal.id);
        }
    }
    
    // Ctrl+Enter to submit form
    if (e.ctrlKey && e.key === 'Enter') {
        if (smoothllmForm.checkValidity()) {
            handleFormSubmit(new Event('submit'));
        }
    }
});
