/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{html,js,jsx}',
    './src/templates/**/*.html',
    // Include web-app content for shared components
    '../../web-app/src/components/ui/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Import design tokens from web-app
        'brand-blue': {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a'
        },
        'warm-gray': {
          50: '#f5f5f4',
          100: '#f0f0ef',
          200: '#e7e5e4',
          300: '#d6d3d1',
          400: '#a8a29e',
          500: '#78716c',
          600: '#57534e',
          700: '#44403c',
          800: '#292524',
          900: '#1c1917'
        },
        'steel-blue': '#475569',
        'purple-accent': '#6366f1',
        'warning-amber': '#f59e0b',
        'status-green': {
          500: '#22c55e',
          600: '#16a34a',
        },
        'status-red': {
          500: '#ef4444',
          600: '#dc2626',
        },
        'status-yellow': {
          500: '#eab308',
          600: '#ca8a04',
        }
      },
      // CSS custom properties for consistency
      backgroundColor: {
        'background': 'var(--background)',
        'card': 'var(--card)',
        'muted': 'var(--muted)',
        'primary': 'var(--primary)',
        'destructive': 'var(--destructive)',
      },
      textColor: {
        'foreground': 'var(--foreground)',
        'muted-foreground': 'var(--muted-foreground)',
        'primary-foreground': 'var(--primary-foreground)',
      },
      borderColor: {
        'border': 'var(--border)',
      }
    },
  },
  plugins: [],
}