// Flash Messages System
class FlashMessages {
    constructor() {
        this.container = null;
        this.timeout = 7000; // 7 seconds
        this.init();
    }

    init() {
        // Create container if it doesn't exist
        if (!document.getElementById('flash-messages-container')) {
            this.container = document.createElement('div');
            this.container.id = 'flash-messages-container';
            this.container.style.cssText = `
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 9999;
                width: 90%;
                max-width: 400px;
                pointer-events: none;
            `;
            document.body.appendChild(this.container);
        } else {
            this.container = document.getElementById('flash-messages-container');
        }
    }

    show(message, type = 'info') {
        const flashId = 'flash-' + Date.now();
        const flashElement = document.createElement('div');
        flashElement.id = flashId;
        flashElement.className = `flash-message flash-${type}`;
        flashElement.style.cssText = `
            background: white;
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            animation: slideIn 0.3s ease;
            pointer-events: auto;
            border-left: 4px solid ${this.getBorderColor(type)};
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
            <span class="flash-icon">${icon}</span>
            <span class="flash-text" style="font-family: 'Quicksand', sans-serif; color: #5D7A5C;">${message}</span>
        `;

        // Close button
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '✕';
        closeBtn.style.cssText = `
            background: none;
            border: none;
            font-size: 18px;
            cursor: pointer;
            color: #B99B7C;
            padding: 0 5px;
            transition: color 0.3s ease;
        `;
        closeBtn.onmouseover = () => closeBtn.style.color = '#5D7A5C';
        closeBtn.onmouseout = () => closeBtn.style.color = '#B99B7C';
        closeBtn.onclick = () => this.dismiss(flashId);

        flashElement.appendChild(contentDiv);
        flashElement.appendChild(closeBtn);
        this.container.appendChild(flashElement);

        // Auto dismiss after timeout
        const timeoutId = setTimeout(() => this.dismiss(flashId), this.timeout);
        
        // Store timeout ID to clear if manually dismissed
        flashElement.dataset.timeoutId = timeoutId;
    }

    dismiss(id) {
        const element = document.getElementById(id);
        if (element) {
            // Clear timeout
            if (element.dataset.timeoutId) {
                clearTimeout(parseInt(element.dataset.timeoutId));
            }
            
            // Animate out
            element.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => {
                if (element.parentNode) {
                    element.remove();
                }
            }, 300);
        }
    }

    getBorderColor(type) {
        const colors = {
            success: '#51cf66',
            error: '#ff6b6b',
            warning: '#ffd43b',
            info: '#9CAF88'
        };
        return colors[type] || colors.info;
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

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateY(-100%);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);