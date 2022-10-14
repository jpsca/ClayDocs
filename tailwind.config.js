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
        'ease-3': 'cubic-bezier(.25, 0, .3, 1)',
        'ease-out-5': 'cubic-bezier(0, 0, 0, 1)',
        'ease-elastic-3': 'cubic-bezier(.5, 1.25, .75, 1.25)',
        'ease-elastic-4': 'cubic-bezier(.5, 1.5, .75, 1.25)',
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
