/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./components/**/*.jinja",
    "./content/**/*.md",
  ],
  darkMode: 'class',
  theme: {
    extend: {
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
