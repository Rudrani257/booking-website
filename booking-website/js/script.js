// ==================== FLASH MESSAGE AUTO-CLOSE ====================
document.addEventListener('DOMContentLoaded', function() {
    // Auto-close flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash');
    
    flashMessages.forEach(flash => {
        setTimeout(() => {
            flash.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => flash.remove(), 300);
        }, 5000);
    });
    
    // Close flash message on click
    const closeButtons = document.querySelectorAll('.close-flash');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const flash = this.parentElement;
            flash.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => flash.remove(), 300);
        });
    });
});

// Slide out animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ==================== FORM VALIDATION ====================
const forms = document.querySelectorAll('.auth-form');

forms.forEach(form => {
    form.addEventListener('submit', function(e) {
        const password = form.querySelector('input[name="password"]');
        const confirmPassword = form.querySelector('input[name="confirm_password"]');
        
        if (confirmPassword && password.value !== confirmPassword.value) {
            e.preventDefault();
            alert('Passwords do not match!');
            confirmPassword.focus();
        }
        
        if (password && password.value.length < 6) {
            e.preventDefault();
            alert('Password must be at least 6 characters long!');
            password.focus();
        }
    });
});