(function(){

const SEL_SWITCH = '.ThemeSwitch'
const STORAGE_KEY = 'theme'
const DARK = 'dark'
const LIGHT = 'light'
const PREFERS_DARK_MEDIA = '(prefers-color-scheme: dark)'
const DISABLED = "disabled"

const theme = {
  value: getColorPreference(),
}

new MutationObserver( (mutationList) => {
  mutationList.forEach( (mutation) => {
    if (mutation.type !== "childList") return
    mutation.addedNodes.forEach( (node) => {
      // Node of type "element"
      if (node.nodeType === 1) {
        addEvents(node)
      }
    })
  })
})
  .observe(document.body, {
    subtree: true,
    childList: true,
    attributes: false,
    characterData: false
  })

function addEvents (root) {
  root.querySelectorAll(SEL_SWITCH)
    .forEach( (node) => {
      node.addEventListener('click', onClick)
    })
}

reflectPreference()
addEvents(document)

// sync with system changes
window
  .matchMedia(PREFERS_DARK_MEDIA)
  .addEventListener('change', ({matches:isDark}) => {
    theme.value = isDark ? DARK : LIGHT
    setPreference()
  })

function onClick (event) {
  const target = event.target
  if (target.getAttribute(DISABLED)) return
  theme.value = theme.value === LIGHT ? DARK : LIGHT
  setPreference()
}

function setPreference () {
  localStorage.setItem(STORAGE_KEY, theme.value)
  reflectPreference()
}

function reflectPreference () {
  if (theme.value === DARK)
    document.documentElement.classList.add(DARK)
  else
    document.documentElement.classList.remove(DARK)
}

function getColorPreference () {
  const value = localStorage.getItem(STORAGE_KEY)
  if (value)
    return value
  else
    return window.matchMedia(PREFERS_DARK_MEDIA).matches
      ? DARK
      : LIGHT
}

})()
