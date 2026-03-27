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
        
        this.strengthLabels = {
            0: 'Very Weak',
            25: 'Weak',
            50: 'Medium',
            75: 'Strong',
            100: 'Very Strong'
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
    
    getStrengthColor(percentage) {
        if (percentage < 25) return '#C47E7E'; // Dusty Rose
        if (percentage < 50) return '#E5B25D'; // Honey
        if (percentage < 75) return '#4A6B4A'; // Deep Sage
        return '#1A3A1A'; // Forest Green
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
    
    // Add container styles if not already present
    addStrengthStyles();
    
    passwordInput.addEventListener('input', () => {
        const password = passwordInput.value;
        const result = strengthChecker.check(password);
        const color = strengthChecker.getStrengthColor(result.strength);
        
        // Update strength bar with gradient
        strengthContainer.innerHTML = `
            <div class="strength-meter">
                <div class="strength-bar-container">
                    <div class="strength-bar">
                        <div class="strength-fill" style="width: ${result.strength}%; background: linear-gradient(90deg, ${color}80, ${color});"></div>
                    </div>
                    <div class="strength-markers">
                        <span class="marker" style="left: 0%"></span>
                        <span class="marker" style="left: 25%"></span>
                        <span class="marker" style="left: 50%"></span>
                        <span class="marker" style="left: 75%"></span>
                        <span class="marker" style="left: 100%"></span>
                    </div>
                </div>
                <div class="strength-label-wrapper">
                    <span class="strength-label" style="color: ${color};">${strengthChecker.getStrengthLabel(result.strength)}</span>
                    <span class="strength-percentage">${Math.round(result.strength)}%</span>
                </div>
            </div>
        `;
        
        // Update criteria list with visual indicators
        let criteriaHtml = '<div class="criteria-grid">';
        for (const [key, criterion] of Object.entries(result.criteria)) {
            const icon = criterion.passed ? '✓' : '○';
            criteriaHtml += `
                <div class="criteria-item ${criterion.passed ? 'passed' : 'failed'}">
                    <span class="criteria-icon" style="background: ${criterion.passed ? color : '#E6E6FA'}">${icon}</span>
                    <span class="criteria-text">${criterion.message}</span>
                </div>
            `;
        }
        criteriaHtml += '</div>';
        criteriaContainer.innerHTML = criteriaHtml;
    });
}

function addStrengthStyles() {
    const styleId = 'password-strength-styles';
    if (document.getElementById(styleId)) return;
    
    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = `
        .strength-meter {
            margin: 15px 0;
        }
        
        .strength-bar-container {
            position: relative;
            margin-bottom: 8px;
        }
        
        .strength-bar {
            width: 100%;
            height: 8px;
            background: rgba(26, 58, 26, 0.1);
            border-radius: 4px;
            overflow: hidden;
            position: relative;
        }
        
        .strength-fill {
            height: 100%;
            transition: width 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            border-radius: 4px;
            position: relative;
            z-index: 1;
        }
        
        .strength-markers {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 8px;
            pointer-events: none;
        }
        
        .marker {
            position: absolute;
            width: 2px;
            height: 8px;
            background: rgba(255, 255, 255, 0.5);
            transform: translateX(-50%);
        }
        
        .strength-label-wrapper {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 4px;
        }
        
        .strength-label {
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .strength-percentage {
            font-size: 0.75rem;
            color: #5A6B7A;
            font-weight: 500;
        }
        
        .criteria-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin: 15px 0;
        }
        
        .criteria-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 10px;
            background: #FAF7F2;
            border-radius: 20px;
            transition: all 0.2s ease;
        }
        
        .criteria-item:hover {
            transform: translateX(3px);
        }
        
        .criteria-item.passed {
            background: rgba(74, 107, 74, 0.1);
        }
        
        .criteria-item.failed {
            opacity: 0.7;
        }
        
        .criteria-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            font-size: 12px;
            font-weight: bold;
            color: white;
        }
        
        .criteria-item.passed .criteria-icon {
            background: #4A6B4A !important;
        }
        
        .criteria-text {
            font-size: 0.813rem;
            color: #2C3E2C;
            font-weight: 500;
        }
        
        .form-input.error {
            border-color: #C47E7E;
            background-color: rgba(196, 126, 126, 0.05);
            animation: shake 0.3s ease;
        }
        
        .form-error {
            color: #C47E7E;
            font-size: 0.813rem;
            margin-top: 6px;
            padding-left: 12px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        
        .form-error::before {
            content: '⚠️';
            font-size: 12px;
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }
        
        .validation-success {
            color: #4A6B4A;
            font-size: 0.813rem;
            margin-top: 6px;
            padding-left: 12px;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        
        .validation-success::before {
            content: '✓';
            font-weight: bold;
        }
    `;
    document.head.appendChild(style);
}

// Form input real-time validation with enhanced feedback
function initRealTimeValidation(input, validationFn) {
    let timeoutId;
    
    input.addEventListener('input', () => {
        clearTimeout(timeoutId);
        
        timeoutId = setTimeout(() => {
            const result = validationFn(input.value);
            
            // Remove existing messages
            removeValidationMessages(input);
            
            if (!result.valid && input.value) {
                // Show error
                input.classList.add('error');
                const error = document.createElement('span');
                error.className = 'form-error';
                error.textContent = result.message;
                input.parentNode.appendChild(error);
                
                // Add error icon to input
                input.style.backgroundImage = 'url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'16\' height=\'16\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'%23C47E7E\' stroke-width=\'2\'%3E%3Ccircle cx=\'12\' cy=\'12\' r=\'10\'/%3E%3Cline x1=\'12\' y1=\'8\' x2=\'12\' y2=\'12\'/%3E%3Cline x1=\'12\' y1=\'16\' x2=\'12.01\' y2=\'16\'/%3E%3C/svg%3E")';
                input.style.backgroundRepeat = 'no-repeat';
                input.style.backgroundPosition = 'right 12px center';
                input.style.paddingRight = '40px';
            } else if (result.valid && input.value) {
                // Show success
                input.classList.remove('error');
                input.classList.add('valid');
                const success = document.createElement('span');
                success.className = 'validation-success';
                success.textContent = '✓ Valid';
                input.parentNode.appendChild(success);
                
                // Add success icon
                input.style.backgroundImage = 'url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'16\' height=\'16\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'%234A6B4A\' stroke-width=\'2\'%3E%3Cpolyline points=\'20 6 9 17 4 12\'/%3E%3C/svg%3E")';
                input.style.backgroundRepeat = 'no-repeat';
                input.style.backgroundPosition = 'right 12px center';
                input.style.paddingRight = '40px';
            } else {
                // Clear styles
                input.classList.remove('error', 'valid');
                input.style.backgroundImage = 'none';
                input.style.paddingRight = '12px';
            }
        }, 300); // Debounce for better UX
    });
    
    input.addEventListener('blur', () => {
        clearTimeout(timeoutId);
        
        const result = validationFn(input.value);
        
        // Remove existing messages
        removeValidationMessages(input);
        
        if (!result.valid && input.value) {
            input.classList.add('error');
            const error = document.createElement('span');
            error.className = 'form-error';
            error.textContent = result.message;
            input.parentNode.appendChild(error);
        } else if (!input.value) {
            input.classList.remove('error', 'valid');
            input.style.backgroundImage = 'none';
            input.style.paddingRight = '12px';
        }
    });
}

function removeValidationMessages(input) {
    const parent = input.parentNode;
    const existingError = parent.querySelector('.form-error');
    const existingSuccess = parent.querySelector('.validation-success');
    if (existingError) existingError.remove();
    if (existingSuccess) existingSuccess.remove();
}