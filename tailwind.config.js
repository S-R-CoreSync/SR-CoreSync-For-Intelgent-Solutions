/**
 * Tailwind CSS configuration for S&R CoreSync project.
 * Custom colors: #1A73E8 (primary), #FF9800 (accent).
 * Font family: Cairo (fallback to system sans-serif).
 */
module.exports = {
  content: [
    './index.html',
    './modules/**/*.js',
    './src/**/*.css',
    './_site.next/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1A73E8',
        accent: '#FF9800',
      },
      fontFamily: {
        sans: ['Cairo', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};