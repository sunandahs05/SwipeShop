// api.js

const API_BASE_URL = '/api';

/**
 * Helper to make API calls using fetch
 */
async function fetchAPI(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {}
    };

    if (data) {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(data);
    }

    // Include credentials to handle Flask sessions properly
    options.credentials = 'include';

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        let result = {};
        
        try {
            result = await response.json();
        } catch(e) {
            console.warn("Response was not JSON");
        }

        if (!response.ok) {
            throw new Error(result.error || `HTTP error! status: ${response.status}`);
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Utility to show error/success messages
 */
function showMessage(elementId, message, isError = true) {
    const el = document.getElementById(elementId);
    if (!el) return;
    
    el.textContent = message;
    el.className = `alert ${isError ? 'alert-error' : 'alert-success'}`;
    el.style.display = 'block';
    
    setTimeout(() => {
        el.style.display = 'none';
    }, 5000);
}

/**
 * Check authentication status (simple check via localStorage or session)
 * A robust app would hit a /api/me endpoint, but we can manage UI state simply here.
 */
function updateNavigation(role = null) {
    document.querySelectorAll('.nav-guest').forEach(el => el.style.display = role ? 'none' : 'inline-block');
    document.querySelectorAll('.nav-auth').forEach(el => el.style.display = role ? 'inline-block' : 'none');
    
    if (role === 'admin') {
        document.querySelectorAll('.nav-admin').forEach(el => el.style.display = 'inline-block');
    } else {
        document.querySelectorAll('.nav-admin').forEach(el => el.style.display = 'none');
    }
    
    if (role === 'seller') {
        document.querySelectorAll('.nav-seller').forEach(el => el.style.display = 'inline-block');
    } else {
        document.querySelectorAll('.nav-seller').forEach(el => el.style.display = 'none');
    }
}

// Automatically update nav on load if user info is stored
document.addEventListener('DOMContentLoaded', () => {
    const role = localStorage.getItem('user_role');
    updateNavigation(role);
});
