// English Tutor - Authentication JavaScript

const API_BASE = '/api';

function getToken() {
    return localStorage.getItem('token');
}

function getUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

function setAuth(token, user) {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
}

function clearAuth() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
}

function isLoggedIn() {
    return !!getToken();
}

async function apiRequest(endpoint, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || 'Request failed');
    }

    return data;
}

async function login(username, password) {
    try {
        const data = await apiRequest('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        setAuth(data.token, data.user);
        return { success: true, user: data.user };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function signup(userData) {
    try {
        const data = await apiRequest('/auth/signup', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
        setAuth(data.token, data.user);
        return { success: true, user: data.user };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

function logout() {
    clearAuth();
    window.location.href = 'index.html';
}

function protectRoute() {
    if (!isLoggedIn()) {
        window.location.href = 'login.html';
    }
}

function setupLogout() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            logout();
        });
    }
}

// Mobile navigation toggle
document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }
});
