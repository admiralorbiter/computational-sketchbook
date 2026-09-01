/**
 * Welcome Card Web Component
 * Example Web Component demonstrating the component architecture
 */
class WelcomeCard extends HTMLElement {
    constructor() {
        super();
    }

    connectedCallback() {
        const title = this.getAttribute('title') || 'Welcome';
        const message = this.getAttribute('message') || 'Welcome to PrimeTime';
        
        this.innerHTML = `
            <div class="welcome-card">
                <h2>${title}</h2>
                <p>${message}</p>
            </div>
        `;
    }
}

// Register the custom element
customElements.define('welcome-card', WelcomeCard);

