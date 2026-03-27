// Flash Messages System - Complete Version
class FlashMessages {
    constructor() {
        this.container = null;
        this.timeout = 7000; // 7 seconds
        this.init();
    }

    init() {
        // Find existing container or create one
        const existingContainer = document.getElementById('flash-messages-container');
        if (existingContainer) {
            this.container = existingContainer;
        } else {
            this.container = document.createElement('div');
            this.container.id = 'flash-messages-container';
            this.container.style.cssText = `
                position: fixed;
                top: 20px;
                left: 0;
                right: 0;
                z-index: 10000;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                pointer-events: none;
            `;
            document.body.appendChild(this.container);
        }
    }

    show(message, type = 'info') {
        const flashId = 'flash-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        const flashElement = document.createElement('div');
        flashElement.id = flashId;
        flashElement.className = `flash-message flash-${type}`;
        
        const colors = this.getColors(type);
        
        flashElement.style.cssText = `
            background: ${colors.background};
            border-radius: 16px;
            padding: 14px 20px;
            margin-bottom: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            animation: slideDown 0.3s ease forwards;
            pointer-events: auto;
            border-left: 4px solid ${colors.border};
            max-width: 450px;
            width: 90%;
        `;

        // Icon based on type
        const icon = this.getIcon(type);

        // Message content
        const contentDiv = document.createElement('div');
        contentDiv.style.cssText = `
            display: flex;
            align-items: center;
            gap: 12px;
            flex: 1;
        `;
        contentDiv.innerHTML = `
            <span class="flash-icon" style="font-size: 1.25rem;">${icon}</span>
            <span class="flash-text" style="font-family: 'Quicksand', sans-serif; color: ${colors.text}; font-weight: 500; line-height: 1.4; font-size: 0.95rem;">${message}</span>
        `;

        // Close button
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '✕';
        closeBtn.className = 'flash-close';
        closeBtn.style.cssText = `
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            color: ${colors.close};
            padding: 0 5px;
            transition: all 0.2s;
            border-radius: 8px;
            opacity: 0.7;
        `;
        closeBtn.onmouseover = () => {
            closeBtn.style.opacity = '1';
            closeBtn.style.backgroundColor = `${colors.close}20`;
        };
        closeBtn.onmouseout = () => {
            closeBtn.style.opacity = '0.7';
            closeBtn.style.backgroundColor = 'transparent';
        };
        closeBtn.onclick = () => this.dismiss(flashId);

        flashElement.appendChild(contentDiv);
        flashElement.appendChild(closeBtn);
        this.container.appendChild(flashElement);

        // Auto dismiss after timeout
        const timeoutId = setTimeout(() => this.dismiss(flashId), this.timeout);
        flashElement.dataset.timeoutId = timeoutId;
        
        // Add progress bar animation
        const progressBar = document.createElement('div');
        progressBar.style.cssText = `
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg, ${colors.border}80, ${colors.border}, ${colors.border}80);
            animation: shrink ${this.timeout/1000}s linear forwards;
        `;
        flashElement.style.position = 'relative';
        flashElement.style.overflow = 'hidden';
        flashElement.appendChild(progressBar);
        
        return flashId;
    }

    getColors(type) {
        const colors = {
            success: {
                background: '#F0F4EA',
                border: '#4A6B4A',
                text: '#2C3E2C',
                close: '#4A6B4A'
            },
            error: {
                background: '#FDF2F2',
                border: '#C47E7E',
                text: '#2C3E2C',
                close: '#C47E7E'
            },
            warning: {
                background: '#FEF5E7',
                border: '#E5B25D',
                text: '#2C3E2C',
                close: '#E5B25D'
            },
            info: {
                background: '#FAF7F2',
                border: '#9CAF88',
                text: '#2C3E2C',
                close: '#9CAF88'
            }
        };
        return colors[type] || colors.info;
    }

    dismiss(id) {
        const element = document.getElementById(id);
        if (element) {
            if (element.dataset.timeoutId) {
                clearTimeout(parseInt(element.dataset.timeoutId));
            }
            element.classList.add('hiding');
            element.style.animation = 'slideUp 0.3s ease forwards';
            setTimeout(() => {
                if (element.parentNode) {
                    element.remove();
                }
            }, 300);
        }
    }

    getIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || icons.info;
    }

    success(message) {
        this.show(message, 'success');
    }

    error(message) {
        this.show(message, 'error');
    }

    warning(message) {
        this.show(message, 'warning');
    }

    info(message) {
        this.show(message, 'info');
    }
}

// Initialize flash messages globally
const flashMessages = new FlashMessages();

// Function to handle existing Django messages
function initDjangoMessages() {
    const existingMessages = document.querySelectorAll('#flash-messages-container .flash-message');
    existingMessages.forEach(function(msg) {
        // Auto-hide after 5 seconds
        setTimeout(function() {
            if (msg.parentNode) {
                msg.classList.add('hiding');
                msg.style.animation = 'slideUp 0.3s ease forwards';
                setTimeout(function() {
                    if (msg.parentNode) msg.remove();
                }, 300);
            }
        }, 5000);
        
        // Ensure close button works
        const closeBtn = msg.querySelector('.flash-close');
        if (closeBtn) {
            closeBtn.onclick = function() {
                msg.classList.add('hiding');
                msg.style.animation = 'slideUp 0.3s ease forwards';
                setTimeout(() => msg.remove(), 300);
            };
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initDjangoMessages();
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideDown {
        from {
            transform: translateY(-100%);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes slideUp {
        from {
            transform: translateY(0);
            opacity: 1;
        }
        to {
            transform: translateY(-100%);
            opacity: 0;
        }
    }
    
    @keyframes shrink {
        from {
            width: 100%;
        }
        to {
            width: 0%;
        }
    }
    
    .flash-message {
        position: relative;
        overflow: hidden;
    }
    
    .flash-message.hiding {
        animation: slideUp 0.3s ease forwards;
    }
    
    @media (max-width: 768px) {
        .flash-message {
            max-width: 90% !important;
            width: 90% !important;
            padding: 12px 16px !important;
        }
        
        .flash-text {
            font-size: 0.85rem !important;
        }
        
        .flash-icon {
            font-size: 1rem !important;
        }
    }
`;
document.head.appendChild(style);