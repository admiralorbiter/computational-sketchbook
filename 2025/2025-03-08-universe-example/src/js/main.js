// Update the main.js file to include the new interactive elements
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the course
    console.log('Course initialized');
    
    // Add smooth scrolling for navigation links
    document.querySelectorAll('nav a').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            window.scrollTo({
                top: targetElement.offsetTop - 70,
                behavior: 'smooth'
            });
        });
    });
    
    // Add animation to sections when they come into view
    const sections = document.querySelectorAll('section');
    
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    sections.forEach(section => {
        observer.observe(section);
    });
    
    // Track progress through the course
    let progress = {
        currentModule: 1,
        completedUnits: []
    };
    
    // Save progress to localStorage
    function saveProgress() {
        localStorage.setItem('universeCourseProg', JSON.stringify(progress));
    }
    
    // Load progress from localStorage
    function loadProgress() {
        const savedProgress = localStorage.getItem('universeCourseProg');
        if (savedProgress) {
            progress = JSON.parse(savedProgress);
            updateProgressUI();
        }
    }
    
    // Update UI based on progress
    function updateProgressUI() {
        // Highlight current module in navigation
        document.querySelectorAll('nav a').forEach((link, index) => {
            if (index + 1 === progress.currentModule) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
        
        // Mark completed units
        progress.completedUnits.forEach(unitId => {
            const unitElement = document.getElementById(unitId);
            if (unitElement) {
                unitElement.classList.add('completed');
            }
        });
    }
    
    // Load saved progress on page load
    loadProgress();
    
    // Initialize interactive elements
    if (typeof createScaleVisualization === 'function') {
        createScaleVisualization();
    }
    
    if (typeof createParallaxDemo === 'function') {
        createParallaxDemo();
    }
    
    if (typeof initializeCepheidCalculator === 'function') {
        initializeCepheidCalculator();
    }
    
    if (typeof initializeRedshiftCalculator === 'function') {
        initializeRedshiftCalculator();
    }
    
    if (typeof initializeHRDiagram === 'function') {
        initializeHRDiagram();
    }
});
