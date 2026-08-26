// src/index.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { Toaster } from 'react-hot-toast';

import { store } from './store';
import App from './App';
import './index.css';

// Apply saved theme class immediately to prevent flash
const savedTheme = localStorage.getItem('aria_theme') || 'dark';
document.documentElement.classList.toggle('dark', savedTheme === 'dark');

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <HelmetProvider>
      <Provider store={store}>
        <BrowserRouter>
          <App />
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#1e293b',
                color:      '#f1f5f9',
                border:     '1px solid rgba(255,255,255,0.1)',
                borderRadius: '12px',
                fontSize:   '14px',
              },
              success: {
                iconTheme: { primary: '#22c55e', secondary: '#1e293b' },
              },
              error: {
                iconTheme: { primary: '#ef4444', secondary: '#1e293b' },
              },
            }}
          />
        </BrowserRouter>
      </Provider>
    </HelmetProvider>
  </React.StrictMode>
);
