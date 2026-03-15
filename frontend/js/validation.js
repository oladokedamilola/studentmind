// Form Validation Utilities

// Password strength checker
class PasswordStrength {
    constructor() {
        this.criteria = {
            minLength: { regex: /.{8,}/, message: 'At least 8 characters' },
            hasNumber: { regex: /[0-9]/, message: 'Contains a number' },
            hasUppercase: { regex: /[A-Z]/, message: 'Contains uppercase letter' },
            hasLowercase: { regex: /[a-z]/, message: 'Contains lowercase letter' }
        };
    }

    check(password) {
        const results = {};
        let strength = 0;
        
        for (const [key, criterion] of Object.entries(this.criteria)) {
            const passed = criterion.regex.test(password);
            results[key] = { passed, message: criterion.message };
            if (passed) strength++;
        }
        
        const percentage = (strength / Object.keys(this.criteria).length) * 100;
        
        return {
            strength: percentage,
            criteria: results,
            isValid: strength === Object.keys(this.criteria).length
        };
    }

    getStrengthLabel(percentage) {
        if (percentage < 25) return 'Very Weak';
        if (percentage < 50) return 'Weak';
        if (percentage < 75) return 'Medium';
        if (percentage < 100) return 'Strong';
        return 'Very Strong';
    }
}

// Matric number validation
function validateMatricNumber(matric) {
    const cleaned = matric.replace(/\s/g, '');
    const regex = /^\d{9,10}$/;
    
    if (!cleaned) {
        return { valid: false, message: 'Matric number is required' };
    }
    
    if (!regex.test(cleaned)) {
        return { valid: false, message: 'Matric number must be 9-10 digits' };
    }
    
    return { valid: true, message: '' };
}

// Email validation (for university email)
function validateUniversityEmail(email) {
    const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(edu|ac\.[a-z]+)$/i;
    
    if (!email) {
        return { valid: false, message: 'Email is required' };
    }
    
    if (!regex.test(email)) {
        return { valid: false, message: 'Please use your university email' };
    }
    
    return { valid: true, message: '' };
}

// Password match validation
function validatePasswordMatch(password, confirmPassword) {
    if (password !== confirmPassword) {
        return { valid: false, message: 'Passwords do not match' };
    }
    return { valid: true, message: '' };
}

// Real-time password strength meter
function initPasswordStrengthMeter(passwordInput, strengthContainer, criteriaContainer) {
    const strengthChecker = new PasswordStrength();
    
    passwordInput.addEventListener('input', () => {
        const password = passwordInput.value;
        const result = strengthChecker.check(password);
        
        // Update strength bar
        strengthContainer.innerHTML = `
            <div class="strength-bar">
                <div class="strength-fill" style="width: ${result.strength}%; background: ${getStrengthColor(result.strength)};"></div>
            </div>
            <span class="strength-label">${strengthChecker.getStrengthLabel(result.strength)}</span>
        `;
        
        // Update criteria list
        let criteriaHtml = '<ul class="criteria-list">';
        for (const [key, criterion] of Object.entries(result.criteria)) {
            const icon = criterion.passed ? '✓' : '✗';
            criteriaHtml += `
                <li class="${criterion.passed ? 'passed' : 'failed'}">
                    <span class="criteria-icon">${icon}</span>
                    <span class="criteria-text">${criterion.message}</span>
                </li>
            `;
        }
        criteriaHtml += '</ul>';
        criteriaContainer.innerHTML = criteriaHtml;
        
        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .strength-bar {
                width: 100%;
                height: 8px;
                background: #E6E6FA;
                border-radius: 4px;
                overflow: hidden;
                margin: 10px 0;
            }
            
            .strength-fill {
                height: 100%;
                transition: width 0.3s ease;
            }
            
            .strength-label {
                font-size: 0.875rem;
                color: #5D7A5C;
                margin-left: 10px;
            }
            
            .criteria-list {
                list-style: none;
                padding: 0;
                margin: 10px 0;
            }
            
            .criteria-list li {
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 5px;
                font-size: 0.875rem;
            }
            
            .criteria-list .passed {
                color: #51cf66;
            }
            
            .criteria-list .failed {
                color: #ff6b6b;
            }
            
            .criteria-icon {
                font-weight: bold;
            }
        `;
        document.head.appendChild(style);
    });
}

function getStrengthColor(percentage) {
    if (percentage < 25) return '#ff6b6b';
    if (percentage < 50) return '#ffd43b';
    if (percentage < 75) return '#51cf66';
    return '#9CAF88';
}

// Form input real-time validation
function initRealTimeValidation(input, validationFn) {
    input.addEventListener('input', () => {
        const result = validationFn(input.value);
        
        // Remove existing error
        const existingError = input.parentNode.querySelector('.form-error');
        if (existingError) existingError.remove();
        
        if (!result.valid && input.value) {
            input.classList.add('error');
            const error = document.createElement('span');
            error.className = 'form-error';
            error.textContent = result.message;
            input.parentNode.appendChild(error);
        } else {
            input.classList.remove('error');
        }
    });
    
    input.addEventListener('blur', () => {
        const result = validationFn(input.value);
        
        // Remove existing error
        const existingError = input.parentNode.querySelector('.form-error');
        if (existingError) existingError.remove();
        
        if (!result.valid) {
            input.classList.add('error');
            const error = document.createElement('span');
            error.className = 'form-error';
            error.textContent = result.message;
            input.parentNode.appendChild(error);
        } else {
            input.classList.remove('error');
        }
    });
}