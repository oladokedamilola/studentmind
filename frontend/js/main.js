// Main JavaScript File

// Preloader
class Preloader {
    constructor() {
        this.preloader = null;
        this.minDisplayTime = 3000; // 3 seconds minimum
        this.startTime = null;
        this.messages = [
            "Creating your safe space...",
            "Warming up the cozy corner...",
            "Preparing your sanctuary...",
            "Almost there...",
            "Setting up calming vibes..."
        ];
    }

    show() {
        this.startTime = Date.now();
        
        // Create preloader if it doesn't exist
        if (!document.getElementById('preloader')) {
            this.preloader = document.createElement('div');
            this.preloader.id = 'preloader';
            
            // Random message
            const randomMessage = this.messages[Math.floor(Math.random() * this.messages.length)];
            
            this.preloader.innerHTML = `
                <div class="preloader-content">
                    <div class="preloader-logo">
                        <svg width="80" height="80" viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="40" cy="40" r="36" stroke="url(#gradient)" stroke-width="3" stroke-dasharray="8 8"/>
                            <path d="M25 40 L35 50 L55 30" stroke="url(#gradient)" stroke-width="4" stroke-linecap="round"/>
                            <defs>
                                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" style="stop-color:#4A6B4A"/>
                                    <stop offset="100%" style="stop-color:#1A3A1A"/>
                                </linearGradient>
                            </defs>
                        </svg>
                    </div>
                    <div class="preloader-text">MindHaven</div>
                    <div class="preloader-spinner">
                        <div class="spinner"></div>
                    </div>
                    <div class="preloader-message">${randomMessage}</div>
                </div>
            `;
            
            // Add styles
            const style = document.createElement('style');
            style.textContent = `
                #preloader {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(135deg, #FAF7F2 0%, #F5F0E8 100%);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 10000;
                    transition: opacity 0.5s ease;
                }
                
                .preloader-content {
                    text-align: center;
                    animation: gentlePulse 2s infinite ease-in-out;
                }
                
                .preloader-logo {
                    margin-bottom: 25px;
                    animation: gentleRotate 4s linear infinite;
                    filter: drop-shadow(0 10px 15px -5px rgba(26, 58, 26, 0.3));
                }
                
                .preloader-text {
                    font-family: 'Nunito', sans-serif;
                    font-size: 32px;
                    font-weight: 700;
                    background: linear-gradient(135deg, #4A6B4A 0%, #1A3A1A 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin-bottom: 25px;
                    letter-spacing: 1px;
                }
                
                .preloader-spinner {
                    margin: 25px 0;
                }
                
                .spinner {
                    width: 50px;
                    height: 50px;
                    border: 3px solid rgba(74, 107, 74, 0.1);
                    border-top: 3px solid #4A6B4A;
                    border-right: 3px solid #C17B5C;
                    border-radius: 50%;
                    margin: 0 auto;
                    animation: spin 1s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
                    box-shadow: 0 0 20px rgba(74, 107, 74, 0.2);
                }
                
                .preloader-message {
                    font-family: 'Quicksand', sans-serif;
                    color: #5A6B7A;
                    font-size: 18px;
                    font-weight: 500;
                    margin-top: 15px;
                }
                
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                
                @keyframes gentlePulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.02); }
                    100% { transform: scale(1); }
                }
                
                @keyframes gentleRotate {
                    0% { transform: rotate(0deg); }
                    25% { transform: rotate(3deg); }
                    75% { transform: rotate(-3deg); }
                    100% { transform: rotate(0deg); }
                }
            `;
            document.head.appendChild(style);
            document.body.appendChild(this.preloader);
        }
    }

    hide() {
        const elapsed = Date.now() - this.startTime;
        const remaining = Math.max(0, this.minDisplayTime - elapsed);
        
        setTimeout(() => {
            if (this.preloader) {
                this.preloader.style.opacity = '0';
                setTimeout(() => {
                    if (this.preloader && this.preloader.parentNode) {
                        this.preloader.remove();
                    }
                }, 500);
            }
        }, remaining);
    }
}

// Initialize preloader
const preloader = new Preloader();

// Show preloader on page load
document.addEventListener('DOMContentLoaded', () => {
    preloader.show();
});

// Hide preloader when page is fully loaded
window.addEventListener('load', () => {
    preloader.hide();
});

// Session Management
class SessionManager {
    constructor() {
        this.timeoutDuration = 25 * 60 * 1000; // 25 minutes
        this.warningDuration = 5 * 60 * 1000; // 5 minutes
        this.timeoutId = null;
        this.warningId = null;
        this.init();
    }

    init() {
        this.resetTimer();
        this.setupEventListeners();
    }

    resetTimer() {
        if (this.timeoutId) clearTimeout(this.timeoutId);
        if (this.warningId) clearTimeout(this.warningId);

        // Show warning after 25 minutes
        this.warningId = setTimeout(() => this.showWarning(), this.timeoutDuration);
        
        // Auto logout after 30 minutes
        this.timeoutId = setTimeout(() => this.logout(), this.timeoutDuration + this.warningDuration);
    }

    setupEventListeners() {
        ['click', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
            document.addEventListener(event, () => this.resetTimer());
        });
    }

    showWarning() {
        // Create and show session timeout modal
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content session-modal">
                <div class="modal-icon">
                    <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #FEF5E7 0%, #FDEDD7 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto;">
                        <span style="font-size: 3rem;">⏰</span>
                    </div>
                </div>
                <h3 style="color: #2C3E2C; margin: 1.5rem 0 0.5rem;">Still There?</h3>
                <p style="color: #5A6B7A; margin-bottom: 1.5rem;">You've been inactive for 25 minutes. You'll be logged out in 5 minutes for your security.</p>
                <div class="modal-actions">
                    <button class="btn btn-secondary" onclick="sessionManager.logoutNow()" style="flex: 1;">Logout Now</button>
                    <button class="btn btn-primary" onclick="sessionManager.stayLoggedIn()" style="flex: 1; background: linear-gradient(135deg, #4A6B4A 0%, #1A3A1A 100%);">Stay Logged In</button>
                </div>
                <div class="timeout-progress" style="margin-top: 1.5rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-size: 0.875rem; color: #5A6B7A;">
                        <span>Session expires in</span>
                        <span class="countdown">5:00</span>
                    </div>
                    <div class="progress-bar" style="height: 4px; background: rgba(74, 107, 74, 0.1); border-radius: 2px; overflow: hidden;">
                        <div class="progress-fill" style="width: 100%; height: 100%; background: linear-gradient(90deg, #E5B25D, #C17B5C); animation: shrink 5s linear forwards;"></div>
                    </div>
                </div>
            </div>
        `;
        
        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(26, 58, 26, 0.5);
                backdrop-filter: blur(8px);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10001;
                animation: fadeIn 0.3s ease;
            }
            
            .modal-content {
                background: white;
                border-radius: 32px;
                padding: 2rem;
                max-width: 400px;
                width: 90%;
                text-align: center;
                animation: slideUp 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
                box-shadow: 0 25px 50px -12px rgba(26, 58, 26, 0.5);
                border: 1px solid rgba(74, 107, 74, 0.1);
            }
            
            .modal-actions {
                display: flex;
                gap: 1rem;
                margin-top: 2rem;
            }
            
            @keyframes slideUp {
                from {
                    transform: translateY(50px);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            @keyframes shrink {
                from { width: 100%; }
                to { width: 0%; }
            }
        `;
        document.head.appendChild(style);
        document.body.appendChild(modal);
        
        // Start countdown
        let timeLeft = 300; // 5 minutes in seconds
        const countdownEl = modal.querySelector('.countdown');
        const timer = setInterval(() => {
            timeLeft--;
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            countdownEl.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
            
            if (timeLeft <= 0) {
                clearInterval(timer);
            }
        }, 1000);
        
        // Store timer to clear if needed
        modal.dataset.timer = timer;
    }

    stayLoggedIn() {
        const modal = document.querySelector('.modal-overlay');
        if (modal && modal.dataset.timer) {
            clearInterval(parseInt(modal.dataset.timer));
        }
        modal?.remove();
        this.resetTimer();
        flashMessages.success('Session extended successfully!');
    }

    logoutNow() {
        const modal = document.querySelector('.modal-overlay');
        if (modal && modal.dataset.timer) {
            clearInterval(parseInt(modal.dataset.timer));
        }
        modal?.remove();
        window.location.href = '/logout';
    }

    logout() {
        flashMessages.warning('Session expired. Please login again.');
        setTimeout(() => {
            window.location.href = '/login';
        }, 2000);
    }
}

// Initialize session manager on authenticated pages
if (document.body.classList.contains('authenticated')) {
    const sessionManager = new SessionManager();
}

// Logout confirmation
function showLogoutConfirm() {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-icon">
                <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #FDF2F2 0%, #FCE8E8 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto;">
                    <span style="font-size: 3rem;">👋</span>
                </div>
            </div>
            <h3 style="color: #2C3E2C; margin: 1.5rem 0 0.5rem;">Leaving So Soon?</h3>
            <p style="color: #5A6B7A; margin-bottom: 1.5rem;">Are you sure you want to logout?</p>
            <div class="modal-actions">
                <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()" style="flex: 1;">Cancel</button>
                <button class="btn btn-primary" onclick="logout()" style="flex: 1; background: linear-gradient(135deg, #C47E7E 0%, #A15D5D 100%);">Logout</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

function logout() {
    flashMessages.success('Logged out successfully!');
    setTimeout(() => {
        window.location.href = '/';
    }, 2000);
}