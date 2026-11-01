/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        charcoal: {
          950: '#070A10',
          900: '#0B0F19',
          850: '#111726',
          800: '#172033',
          700: '#1E293B',
          600: '#334155'
        },
        auto: {
          blue: '#3B82F6',
          cyan: '#06B6D4',
          amber: '#F59E0B',
          red: '#EF4444',
          emerald: '#10B981'
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
