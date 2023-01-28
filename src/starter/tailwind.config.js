/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './content/**/*.mdx',
    './content/**/*.jinja',
    './components/**/*.jinja',
    './static/**/*.js',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'accent': 'var(--accent)',
        'accent-darker': 'var(--accent-darker)',
      },
    },
  },
}
