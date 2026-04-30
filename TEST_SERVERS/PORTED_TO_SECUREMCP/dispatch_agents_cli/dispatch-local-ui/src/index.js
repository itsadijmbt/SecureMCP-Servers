// Import our CSS
import './styles.css';

// Import React and ReactDOM
import React from 'react';
import { createRoot } from 'react-dom/client';

// Import our main App component
import App from './components/App';

// Initialize React application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dispatch Local UI - Pure React Mode');

    // Mount the React app
    const rootElement = document.getElementById('root');
    if (rootElement) {
        const root = createRoot(rootElement);
        root.render(React.createElement(App));
    } else {
        console.error('Failed to find root element for React app');
    }
});