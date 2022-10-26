function setTheme () {
  /* This function needs to be executed as soon as possible to prevent
  * a flash of the light theme when the dark theme was previously selected
  */
  const STORAGE_KEY = 'theme'
  const DARK = 'dark'
  const LIGHT = 'light'
  const PREFERS_DARK_MEDIA = '(prefers-color-scheme: dark)'

  function getColorPreference () {
    return localStorage.getItem(STORAGE_KEY)
  }

  function reflectPreference () {
    const value = getColorPreference ()
    if (value === DARK)
      document.documentElement.classList.add(DARK)
    else
      document.documentElement.classList.remove(DARK)
  }

  reflectPreference()
}
setTheme()
