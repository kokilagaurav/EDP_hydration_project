function initHydrationTracker() {
    const STORAGE_KEY = 'hydrationData';
    const progressBar = document.getElementById('hydrationProgress'); // Changed selector

    function getStoredData() {
        const stored = localStorage.getItem(STORAGE_KEY);
        return stored ? JSON.parse(stored) : null;
    }

    function isNewDay(timestamp) {
        const lastDate = new Date(timestamp);
        const currentDate = new Date();
        return lastDate.getDate() !== currentDate.getDate() ||
               lastDate.getMonth() !== currentDate.getMonth() ||
               lastDate.getFullYear() !== currentDate.getFullYear();
    }

    function resetProgress() {
        const data = {
            progress: 0,
            lastUpdated: new Date().getTime()
        };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
        
        // Reset both the value and the UI
        if (progressBar) {
            progressBar.value = 0;
            progressBar.classList.add('resetting');
            
            // Update the current intake display
            const currentIntakeValue = document.getElementById('currentIntakeValue');
            if (currentIntakeValue) currentIntakeValue.textContent = '0';
        }
        
        // Show reset message
        const message = document.createElement('div');
        message.className = 'reset-message';
        message.textContent = 'Progress reset for new day';
        progressBar.parentElement.appendChild(message);
        setTimeout(() => message.classList.add('show'), 100);
        setTimeout(() => {
            message.classList.remove('show');
            setTimeout(() => message.remove(), 300);
        }, 3000);
    }

    function checkAndResetProgress() {
        const data = getStoredData();
        if (!data || !progressBar) {
            resetProgress();
            return;
        }

        if (isNewDay(data.lastUpdated)) {
            resetProgress();
        } else {
            progressBar.value = data.progress;
        }
    }

    // Initial check
    if (progressBar) {
        checkAndResetProgress();
        // Check periodically
        setInterval(checkAndResetProgress, 60000); // Check every minute
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initHydrationTracker);
