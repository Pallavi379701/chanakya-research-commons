/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        chanakya: {
          navy: '#0f172a',
          dark: '#1e293b',
          gold: '#f59e0b',
          amber: '#d97706',
          blue: '#2563eb',
          light: '#f8fafc'
        }
      }
    },
  },
  plugins: [],
}
