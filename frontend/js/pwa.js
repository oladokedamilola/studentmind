// PWA Installation Handler for Django
class PWAInstaller {
    constructor() {
        this.deferredPrompt = null;
        this.isInstalled = false;
        this.hasShownPrompt = false;
        this.installButton = null;
        this.init();
    }

    init() {
        this.checkIfInstalled();
        
        window.addEventListener('beforeinstallprompt', (e) => {
            console.log('beforeinstallprompt event fired');
            e.preventDefault();
            this.deferredPrompt = e;
            
            if (!this.hasShownPrompt && !this.isInstalled) {
                setTimeout(() => this.showInstallPrompt(), 2000);
            }
        });
        
        window.addEventListener('appinstalled', () => {
            console.log('App was installed');
            this.isInstalled = true;
            this.hasShownPrompt = true;
            this.hideInstallUI();
            this.deferredPrompt = null;
            
            if (typeof flashMessages !== 'undefined') {
                flashMessages.success('MindHaven installed successfully! You can now access it from your home screen.');
            }
        });
        
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.checkIfInstalled();
            }
        });
    }
    
    checkIfInstalled() {
        if (window.matchMedia('(display-mode: standalone)').matches || 
            window.navigator.standalone === true) {
            this.isInstalled = true;
            this.hideInstallUI();
        }
    }
    
    showInstallPrompt() {
        if (this.isInstalled || this.hasShownPrompt) return;
        
        const lastPrompt = localStorage.getItem('pwa_last_prompt');
        const now = Date.now();
        
        if (lastPrompt && (now - parseInt(lastPrompt)) < 7 * 24 * 60 * 60 * 1000) {
            return;
        }
        
        this.createInstallUI();
        this.hasShownPrompt = true;
        localStorage.setItem('pwa_last_prompt', now.toString());
    }
    
    createInstallUI() {
        if (document.getElementById('pwa-install-banner')) return;
        
        const banner = document.createElement('div');
        banner.id = 'pwa-install-banner';
        banner.innerHTML = `
            <div style="
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                width: 90%;
                max-width: 400px;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.2);
                padding: 16px 20px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 15px;
                z-index: 10001;
                animation: slideUpBanner 0.3s ease;
                border-left: 4px solid #4A6B4A;
            ">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <img src="/static/images/fav.png" alt="MindHaven" style="width: 48px; height: 48px; border-radius: 12px;">
                    <div>
                        <strong style="color: #2C3E2C; font-size: 1rem;">Install MindHaven</strong>
                        <p style="color: #5A6B7A; font-size: 0.8rem; margin: 0;">Get quick access from your home screen</p>
                    </div>
                </div>
                <div style="display: flex; gap: 8px;">
                    <button id="pwa-install-btn" style="
                        background: linear-gradient(135deg, #4A6B4A 0%, #1A3A1A 100%);
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 30px;
                        font-weight: 600;
                        cursor: pointer;
                        font-size: 0.85rem;
                    ">Install</button>
                    <button id="pwa-close-btn" style="
                        background: none;
                        border: none;
                        font-size: 20px;
                        cursor: pointer;
                        color: #B99B7C;
                        padding: 0 5px;
                    ">✕</button>
                </div>
            </div>
            <style>
                @keyframes slideUpBanner {
                    from {
                        transform: translateX(-50%) translateY(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(-50%) translateY(0);
                        opacity: 1;
                    }
                }
                @keyframes slideOutBanner {
                    from {
                        transform: translateX(-50%) translateY(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateX(-50%) translateY(100%);
                        opacity: 0;
                    }
                }
            </style>
        `;
        
        document.body.appendChild(banner);
        
        document.getElementById('pwa-install-btn')?.addEventListener('click', () => this.installApp());
        document.getElementById('pwa-close-btn')?.addEventListener('click', () => this.hideInstallUI());
        
        this.installButton = banner;
    }
    
    hideInstallUI() {
        if (this.installButton) {
            this.installButton.style.animation = 'slideOutBanner 0.3s ease forwards';
            setTimeout(() => {
                this.installButton?.remove();
                this.installButton = null;
            }, 300);
        }
    }
    
    installApp() {
        if (!this.deferredPrompt) return;
        
        this.deferredPrompt.prompt();
        this.deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                this.hideInstallUI();
            }
            this.deferredPrompt = null;
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (!window.matchMedia('(display-mode: standalone)').matches) {
        window.pwaInstaller = new PWAInstaller();
    }
});