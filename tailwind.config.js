/** @type {import('tailwindcss').Config} */
const colors = require('tailwindcss/colors')

module.exports = {
  content: [
    "./components/**/*.jinja",
    "./content/**/*.md",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'light-text': colors.zinc['800'],
        'light-accent': colors.sky['500'],
        'light-bg': colors.white,
        'dark-text': colors.zinc['200'],
        'dark-accent': colors.sky['400'],
        'dark-bg': colors.zinc['800'],
      },
      transitionTimingFunction: {
        // https://github.com/argyleink/open-props/blob/main/src/props.easing.css
        'io-3': 'var(--ease-3)',
        'out-5': 'var(--ease-out-5)',
        'elastic-3': 'var(--ease-elastic-3)',
        'elastic-4': 'var(--ease-elastic-4)',
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
