/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./components/**/*.jinja",
    "./content/**/*.md",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
