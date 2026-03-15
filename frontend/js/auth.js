// Authentication API calls

const API_BASE_URL = '/api/university';

// Verify matric number
async function verifyMatricNumber(matricNumber) {
    try {
        const response = await fetch(`${API_BASE_URL}/verify-matric/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ matric_number: matricNumber })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Verification failed');
        }
        
        return { success: true, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Create password (complete registration)
async function createPassword(matricNumber, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/create-password/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                matric_number: matricNumber,
                password: password 
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Account creation failed');
        }
        
        return { success: true, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Login
async function login(matricNumber, password, rememberMe = false) {
    try {
        const response = await fetch(`${API_BASE_URL}/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                matric_number: matricNumber,
                password: password,
                remember_me: rememberMe
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Login failed');
        }
        
        return { success: true, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Logout
async function logout() {
    try {
        const response = await fetch(`${API_BASE_URL}/logout/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Logout failed');
        }
        
        return { success: true, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Get current user
async function getCurrentUser() {
    try {
        const response = await fetch(`${API_BASE_URL}/me/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Failed to get user info');
        }
        
        return { success: true, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Check session
async function checkSession() {
    try {
        const response = await fetch(`${API_BASE_URL}/check-session/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Session invalid');
        }
        
        return { success: true, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}