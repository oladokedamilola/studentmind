// Authentication API calls with enhanced error handling and loading states

// Updated API_BASE_URL to match your Django URL structure
// Option 1: If you keep current structure (with double /api/)
const API_BASE_URL = '/api/accounts/api';

// Option 2: If you simplify URLs (recommended - uncomment if you make the URL change)
// const API_BASE_URL = '/api/accounts';

// Request interceptor for common headers and loading states
async function apiRequest(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin', // Include cookies for session
    };

    const mergedOptions = { ...defaultOptions, ...options };
    
    // Add CSRF token if available (for Django)
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
        mergedOptions.headers['X-CSRFToken'] = csrfToken;
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, mergedOptions);
        
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        let data;
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            data = { message: await response.text() };
        }

        if (!response.ok) {
            // Handle specific HTTP status codes
            switch (response.status) {
                case 401:
                    // Unauthorized - redirect to login
                    if (!window.location.pathname.includes('/login')) {
                        flashMessages.warning('Session expired. Please login again.');
                        setTimeout(() => {
                            window.location.href = '/login';
                        }, 2000);
                    }
                    break;
                case 403:
                    flashMessages.error('You don\'t have permission to perform this action.');
                    break;
                case 429:
                    flashMessages.warning('Too many attempts. Please try again later.');
                    break;
                case 500:
                    flashMessages.error('Server error. Please try again later.');
                    break;
            }
            
            // Extract error message from response
            const errorMessage = data.message || data.error || data.detail || getErrorMessage(response.status);
            throw new Error(errorMessage);
        }

        return { success: true, data };
    } catch (error) {
        // Network errors
        if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
            return { 
                success: false, 
                error: 'Network error. Please check your connection.' 
            };
        }
        
        return { success: false, error: error.message };
    }
}

// Helper to get CSRF cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Error message mapper
function getErrorMessage(status) {
    const errors = {
        400: 'Bad request. Please check your input.',
        401: 'Authentication required.',
        403: 'Access denied.',
        404: 'Resource not found.',
        429: 'Too many requests. Please slow down.',
        500: 'Server error. Please try again later.',
        503: 'Service unavailable. Please try again later.'
    };
    return errors[status] || 'An unexpected error occurred.';
}

// Password strength checker class
class PasswordStrength {
    constructor() {
        this.requirements = [
            { regex: /.{8,}/, message: 'At least 8 characters' },
            { regex: /[A-Z]/, message: 'At least one uppercase letter' },
            { regex: /[a-z]/, message: 'At least one lowercase letter' },
            { regex: /[0-9]/, message: 'At least one number' }
        ];
    }
    
    check(password) {
        const results = this.requirements.map(req => ({
            passed: req.regex.test(password),
            message: req.message
        }));
        
        const score = results.filter(r => r.passed).length;
        const strength = score === 4 ? 'strong' : score >= 2 ? 'medium' : 'weak';
        
        return {
            isValid: score === 4,
            score: score,
            strength: strength,
            results: results
        };
    }
}

// Verify matric number
async function verifyMatricNumber(matricNumber) {
    // Show loading state
    const loadingToast = flashMessages.loading?.('Verifying your matric number...');
    
    try {
        const result = await apiRequest('/verify-matric/', {
            method: 'POST',
            body: JSON.stringify({ matric_number: matricNumber })
        });
        
        if (result.success) {
            flashMessages.success('Matric number verified successfully!');
            
            // Store student info in session storage for confirmation page
            if (result.data.student) {
                sessionStorage.setItem('verified_student', JSON.stringify(result.data.student));
            }
        } else {
            flashMessages.error(result.error || 'Verification failed');
        }
        
        return result;
    } finally {
        // Clear loading state
        if (loadingToast && loadingToast.dismiss) loadingToast.dismiss();
    }
}

// Create password (complete registration)
async function createPassword(matricNumber, email, password, confirmPassword) {
    // Validate passwords match
    if (password !== confirmPassword) {
        flashMessages.error('Passwords do not match');
        return { success: false, error: 'Passwords do not match' };
    }
    
    // Validate password strength
    const strengthChecker = new PasswordStrength();
    const strengthResult = strengthChecker.check(password);
    
    if (!strengthResult.isValid) {
        flashMessages.error('Please ensure your password meets all requirements.');
        return { success: false, error: 'Password does not meet requirements' };
    }
    
    const loadingToast = flashMessages.loading?.('Creating your account...');
    
    try {
        const result = await apiRequest('/create-password/', {
            method: 'POST',
            body: JSON.stringify({ 
                matric_number: matricNumber,
                email: email,
                password: password,
                confirm_password: confirmPassword
            })
        });
        
        if (result.success) {
            flashMessages.success('Account created successfully! Please check your email to verify.');
            
            // Clear stored student info
            sessionStorage.removeItem('verified_student');
            
            // Redirect to verification sent page
            setTimeout(() => {
                window.location.href = '/email-verification-sent';
            }, 2000);
        } else {
            // Handle field-specific errors
            if (result.data && result.data.errors) {
                Object.keys(result.data.errors).forEach(field => {
                    flashMessages.error(`${field}: ${result.data.errors[field].join(', ')}`);
                });
            } else {
                flashMessages.error(result.error || 'Account creation failed');
            }
        }
        
        return result;
    } finally {
        if (loadingToast && loadingToast.dismiss) loadingToast.dismiss();
    }
}

// Login
async function login(matricNumber, password, rememberMe = false) {
    const loadingToast = flashMessages.loading?.('Logging you in...');
    
    try {
        const result = await apiRequest('/login/', {
            method: 'POST',
            body: JSON.stringify({ 
                matric_number: matricNumber,
                password: password,
                remember_me: rememberMe
            })
        });
        
        if (result.success) {
            flashMessages.success('Login successful!');
            
            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
        } else {
            // Handle login errors
            if (result.data && result.data.errors) {
                const errorMsg = Object.values(result.data.errors).flat().join(', ');
                flashMessages.error(errorMsg);
            } else {
                flashMessages.error(result.error || 'Login failed');
            }
        }
        
        return result;
    } finally {
        if (loadingToast && loadingToast.dismiss) loadingToast.dismiss();
    }
}

// Logout
async function logout() {
    const loadingToast = flashMessages.loading?.('Logging out...');
    
    try {
        const result = await apiRequest('/logout/', {
            method: 'POST'
        });
        
        if (result.success) {
            flashMessages.success('Logged out successfully!');
            
            // Redirect to home
            setTimeout(() => {
                window.location.href = '/';
            }, 1000);
        }
        
        return result;
    } finally {
        if (loadingToast && loadingToast.dismiss) loadingToast.dismiss();
    }
}

// Get current user
async function getCurrentUser() {
    const result = await apiRequest('/me/', {
        method: 'GET'
    });
    
    return result;
}

// Check session
async function checkSession() {
    const result = await apiRequest('/check-session/', {
        method: 'POST'
    });
    
    return result;
}

// Forgot password request
async function forgotPassword(matricNumber) {
    const loadingToast = flashMessages.loading?.('Processing your request...');
    
    try {
        const result = await apiRequest('/forgot-password/', {
            method: 'POST',
            body: JSON.stringify({ matric_number: matricNumber })
        });
        
        if (result.success) {
            flashMessages.success('If an account exists, you will receive a password reset email.');
        } else {
            flashMessages.error(result.error || 'Request failed');
        }
        
        return result;
    } finally {
        if (loadingToast && loadingToast.dismiss) loadingToast.dismiss();
    }
}

// Resend verification email
async function resendVerification(matricNumber) {
    const loadingToast = flashMessages.loading?.('Sending verification email...');
    
    try {
        const result = await apiRequest('/resend-verification/', {
            method: 'POST',
            body: JSON.stringify({ matric_number: matricNumber })
        });
        
        if (result.success) {
            flashMessages.success('Verification email sent!');
        } else {
            flashMessages.error(result.error || 'Failed to send verification email');
        }
        
        return result;
    } finally {
        if (loadingToast && loadingToast.dismiss) loadingToast.dismiss();
    }
}

// Change password (when logged in)
async function changePassword(oldPassword, newPassword, confirmPassword) {
    if (newPassword !== confirmPassword) {
        flashMessages.error('New passwords do not match');
        return { success: false, error: 'Passwords do not match' };
    }
    
    const loadingToast = flashMessages.loading?.('Changing password...');
    
    try {
        const result = await apiRequest('/change-password/', {
            method: 'POST',
            body: JSON.stringify({
                old_password: oldPassword,
                new_password: newPassword,
                confirm_password: confirmPassword
            })
        });
        
        if (result.success) {
            flashMessages.success('Password changed successfully!');
        } else {
            flashMessages.error(result.error || 'Password change failed');
        }
        
        return result;
    } finally {
        if (loadingToast && loadingToast.dismiss) loadingToast.dismiss();
    }
}

// Export all functions
window.AuthAPI = {
    verifyMatricNumber,
    createPassword,
    login,
    logout,
    getCurrentUser,
    checkSession,
    forgotPassword,
    resendVerification,
    changePassword,
    PasswordStrength
};