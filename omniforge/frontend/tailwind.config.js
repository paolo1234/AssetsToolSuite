/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // OmniForge Dark Theme
        'of-bg': {
          900: '#0d0f14',
          800: '#141720',
          700: '#1a1e2c',
          600: '#222738',
        },
        'of-surface': {
          DEFAULT: '#1e2233',
          hover: '#252a3e',
          active: '#2c3249',
        },
        'of-border': {
          DEFAULT: '#2a2f42',
          focus: '#4a5278',
        },
        'of-accent': {
          DEFAULT: '#6c5ce7',
          hover: '#7d6ff0',
          light: '#a29bfe',
        },
        'of-success': '#00b894',
        'of-warning': '#fdcb6e',
        'of-danger': '#ff7675',
        'of-info': '#74b9ff',
        'of-text': {
          DEFAULT: '#e4e6ed',
          muted: '#8a8fa8',
          dim: '#5a5f78',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      gridTemplateColumns: {
        'workspace': '250px 1fr 300px',
      },
      gridTemplateRows: {
        'workspace': '48px 1fr 28px',
      },
    },
  },
  plugins: [],
};
