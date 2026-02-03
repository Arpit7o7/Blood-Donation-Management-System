// Landing Page JavaScript

// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// Registration redirect function
function redirectToRegistration(role) {
    const registrationPages = {
        'donor': 'auth/donor-register.html',
        'hospital': 'auth/hospital-register.html',
        'camp': 'auth/camp-register.html',
        'patient': 'auth/patient-register.html'
    };
    
    const page = registrationPages[role];
    if (page) {
        window.location.href = page;
    } else {
        console.error('Invalid role:', role);
    }
}

// Smooth scrolling for navigation links
document.addEventListener('DOMContentLoaded', function() {
    // Add smooth scrolling to navigation links
    const navLinks = document.querySelectorAll('.nav-link[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add animation to action buttons
    const actionButtons = document.querySelectorAll('.action-buttons .btn');
    
    actionButtons.forEach((button, index) => {
        button.style.animationDelay = `${index * 0.1}s`;
        button.classList.add('fade-in-up');
    });
    
    // Add intersection observer for step cards animation
    const stepCards = document.querySelectorAll('.step-card');
    
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    stepCards.forEach(card => {
        observer.observe(card);
    });
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in-up {
        animation: fadeInUp 0.6s ease-out forwards;
        opacity: 0;
    }
    
    .step-card {
        opacity: 0;
        transform: translateY(30px);
        transition: all 0.6s ease-out;
    }
    
    .step-card.animate-in {
        opacity: 1;
        transform: translateY(0);
    }
    
    /* Mobile menu toggle (for future implementation) */
    .mobile-menu-toggle {
        display: none;
        background: none;
        border: none;
        color: var(--white);
        font-size: 1.5rem;
        cursor: pointer;
    }
    
    @media (max-width: 768px) {
        .mobile-menu-toggle {
            display: block;
        }
        
        .nav-menu {
            display: none;
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: var(--dark-bg);
            flex-direction: column;
            padding: var(--spacing-4);
            box-shadow: var(--shadow-lg);
        }
        
        .nav-menu.active {
            display: flex;
        }
        
        .nav-menu .nav-link {
            padding: var(--spacing-3) 0;
            border-bottom: 1px solid var(--gray-700);
        }
        
        .nav-menu .nav-link:last-child {
            border-bottom: none;
        }
    }
`;

document.head.appendChild(style);

// Utility functions
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 24px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        transform: translateX(100%);
        transition: transform 0.3s ease-in-out;
        max-width: 300px;
        word-wrap: break-word;
    `;
    
    // Set background color based on type
    const colors = {
        'success': '#10b981',
        'error': '#ef4444',
        'warning': '#f59e0b',
        'info': '#3b82f6'
    };
    
    notification.style.backgroundColor = colors[type] || colors.info;
    
    // Add to DOM
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 5 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 5000);
}

// Check if user is already logged in
function checkAuthStatus() {
    const token = localStorage.getItem('access_token');
    const userRole = localStorage.getItem('user_role');
    
    if (token && userRole) {
        // User is logged in, could redirect to dashboard
        console.log('User is already logged in as:', userRole);
        // Uncomment below to auto-redirect logged in users
        // window.location.href = `${userRole}/dashboard.html`;
    }
}

// Call auth check on page load
document.addEventListener('DOMContentLoaded', checkAuthStatus);

// Export functions for use in other scripts
window.BloodSystemLanding = {
    redirectToRegistration,
    showNotification,
    checkAuthStatus,
    API_BASE_URL
};