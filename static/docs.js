function setTheme () {
  /* This function needs to be executed as soon as possible to prevent
  * a flash of the light theme when the dark theme was previously selected
  */
  const STORAGE_KEY = 'theme'
  const DARK = 'dark'
  const LIGHT = 'light'

  function getColorPreference () {
    return localStorage.getItem(STORAGE_KEY)
  }

  function reflectPreference () {
    const value = getColorPreference ()
    if (value === DARK) {
      document.documentElement.classList.add(DARK)
      document.documentElement.classList.remove(LIGHT)
    } else {
      document.documentElement.classList.add(LIGHT)
      document.documentElement.classList.remove(DARK)
    }
  }

  reflectPreference()
}
setTheme()
