/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // ARIA Brand Colors
        aria: {
          50:  '#fff1f1',
          100: '#ffe1e1',
          200: '#ffc8c8',
          300: '#ffa0a0',
          400: '#ff6b6b',
          500: '#ff3b3b',
          600: '#ed1a1a',
          700: '#c81111',
          800: '#a51313',
          900: '#881717',
          950: '#4b0606',
        },
        // Emergency severity palette
        critical: {
          DEFAULT: '#ef4444',
          light: '#fee2e2',
          dark:  '#991b1b',
        },
        high: {
          DEFAULT: '#f97316',
          light: '#ffedd5',
          dark:  '#9a3412',
        },
        medium: {
          DEFAULT: '#eab308',
          light: '#fef9c3',
          dark:  '#713f12',
        },
        low: {
          DEFAULT: '#22c55e',
          light: '#dcfce7',
          dark:  '#14532d',
        },
        // Dashboard surface colors
        surface: {
          50:  '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          700: '#334155',
          800: '#1e293b',
          850: '#172033',
          900: '#0f172a',
          950: '#090f1f',
        },
        // Status colors
        status: {
          active:     '#22c55e',
          inactive:   '#94a3b8',
          responding: '#3b82f6',
          alert:      '#ef4444',
          standby:    '#f59e0b',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        display: ['Inter', 'sans-serif'],
      },
      fontSize: {
        '2xs': ['0.625rem', { lineHeight: '1rem' }],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '112': '28rem',
        '128': '32rem',
      },
      borderRadius: {
        '4xl': '2rem',
      },
      boxShadow: {
        'glow-red':  '0 0 20px rgba(239, 68, 68, 0.35)',
        'glow-blue': '0 0 20px rgba(59, 130, 246, 0.35)',
        'glow-green':'0 0 20px rgba(34, 197, 94, 0.35)',
        'glass':     '0 8px 32px rgba(0, 0, 0, 0.37)',
        'card':      '0 4px 24px rgba(0, 0, 0, 0.25)',
        'sidebar':   '4px 0 24px rgba(0, 0, 0, 0.3)',
      },
      backdropBlur: {
        xs: '2px',
      },
      animation: {
        'pulse-slow':     'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow':      'spin 3s linear infinite',
        'ping-slow':      'ping 2s cubic-bezier(0, 0, 0.2, 1) infinite',
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'slide-in-left':  'slideInLeft 0.3s ease-out',
        'slide-up':       'slideUp 0.3s ease-out',
        'fade-in':        'fadeIn 0.2s ease-out',
        'bounce-dot':     'bounceDot 1.4s ease-in-out infinite',
      },
      keyframes: {
        slideInRight: {
          from: { transform: 'translateX(100%)', opacity: '0' },
          to:   { transform: 'translateX(0)',    opacity: '1' },
        },
        slideInLeft: {
          from: { transform: 'translateX(-100%)', opacity: '0' },
          to:   { transform: 'translateX(0)',     opacity: '1' },
        },
        slideUp: {
          from: { transform: 'translateY(20px)', opacity: '0' },
          to:   { transform: 'translateY(0)',    opacity: '1' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to:   { opacity: '1' },
        },
        bounceDot: {
          '0%, 80%, 100%': { transform: 'scale(0)' },
          '40%':           { transform: 'scale(1)' },
        },
      },
      backgroundImage: {
        'gradient-radial':    'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic':     'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'grid-dark':          'linear-gradient(rgba(255,255,255,.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.03) 1px, transparent 1px)',
        'grid-light':         'linear-gradient(rgba(0,0,0,.05) 1px, transparent 1px), linear-gradient(90deg, rgba(0,0,0,.05) 1px, transparent 1px)',
      },
      backgroundSize: {
        'grid': '40px 40px',
      },
    },
  },
  plugins: [],
};
