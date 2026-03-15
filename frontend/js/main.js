// Main JavaScript File

// Preloader
class Preloader {
    constructor() {
        this.preloader = null;
        this.minDisplayTime = 3000; // 3 seconds minimum
        this.startTime = null;
    }

    show() {
        this.startTime = Date.now();
        
        // Create preloader if it doesn't exist
        if (!document.getElementById('preloader')) {
            this.preloader = document.createElement('div');
            this.preloader.id = 'preloader';
            this.preloader.innerHTML = `
                <div class="preloader-content">
                    <div class="preloader-logo">
                        <svg width="60" height="60" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="30" cy="30" r="28" stroke="#9CAF88" stroke-width="2" stroke-dasharray="8 8"/>
                            <path d="M20 30 L27 37 L40 24" stroke="#5D7A5C" stroke-width="3" stroke-linecap="round"/>
                        </svg>
                    </div>
                    <div class="preloader-text">MindHaven</div>
                    <div class="preloader-spinner">
                        <div class="spinner"></div>
                    </div>
                    <div class="preloader-message">Creating your safe space...</div>
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
                    background: #FDF6E9;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 10000;
                    transition: opacity 0.5s ease;
                }
                
                .preloader-content {
                    text-align: center;
                    animation: pulse 2s infinite;
                }
                
                .preloader-logo {
                    margin-bottom: 20px;
                    animation: rotate 3s linear infinite;
                }
                
                .preloader-text {
                    font-family: 'Nunito', sans-serif;
                    font-size: 24px;
                    font-weight: 600;
                    color: #5D7A5C;
                    margin-bottom: 20px;
                }
                
                .preloader-spinner {
                    margin: 20px 0;
                }
                
                .spinner {
                    width: 40px;
                    height: 40px;
                    border: 3px solid #E6E6FA;
                    border-top: 3px solid #9CAF88;
                    border-radius: 50%;
                    margin: 0 auto;
                    animation: spin 1s linear infinite;
                }
                
                .preloader-message {
                    font-family: 'Quicksand', sans-serif;
                    color: #B99B7C;
                    font-size: 16px;
                }
                
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                    100% { transform: scale(1); }
                }
                
                @keyframes rotate {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
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
                <div class="modal-icon">⏰</div>
                <h3>Still There?</h3>
                <p>You've been inactive for 25 minutes. You'll be logged out in 5 minutes for your security.</p>
                <div class="modal-actions">
                    <button class="btn btn-secondary" onclick="sessionManager.logoutNow()">Logout Now</button>
                    <button class="btn btn-primary" onclick="sessionManager.stayLoggedIn()">Stay Logged In</button>
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
                background: rgba(0,0,0,0.5);
                backdrop-filter: blur(3px);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10001;
            }
            
            .modal-content {
                background: white;
                border-radius: 24px;
                padding: 2rem;
                max-width: 400px;
                width: 90%;
                text-align: center;
                animation: slideUp 0.3s ease;
            }
            
            .modal-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
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
        `;
        document.head.appendChild(style);
        document.body.appendChild(modal);
    }

    stayLoggedIn() {
        document.querySelector('.modal-overlay')?.remove();
        this.resetTimer();
        flashMessages.success('Session extended successfully!');
    }

    logoutNow() {
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
            <div class="modal-icon">👋</div>
            <h3>Leaving So Soon?</h3>
            <p>Are you sure you want to logout?</p>
            <div class="modal-actions">
                <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                <button class="btn btn-primary" onclick="logout()">Logout</button>
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