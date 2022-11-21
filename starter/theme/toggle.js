(function(){

const ATTR_TOGGLE_CLASS = "data-toggle"
const SEL_TOGGLE = `[${ATTR_TOGGLE_CLASS}]`

const ATTR_SHOW_DIALOG = "data-show-dialog"
const SEL_SHOW = `[${ATTR_SHOW_DIALOG}]`

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
  root.querySelectorAll(SEL_TOGGLE)
    .forEach( (node) => {
      node.addEventListener("click", onToggleClick)
    })
  root.querySelectorAll(SEL_SHOW)
  .forEach( (node) => {
    node.addEventListener("click", onShowClick)
  })
}

addEvents(document)

function onToggleClick (event) {
  const target = event.target.closest(SEL_TOGGLE)
  const [ sel, value ] = (target.getAttribute(ATTR_TOGGLE_CLASS) || "").split("|")
  if (!!sel && !!value) { toggle(sel, value) }
}

function toggle (sel, value) {
  for (const node of document.querySelectorAll(sel)) {
    toggleAttribute(node, value)
  }
}

function toggleAttribute (node, value) {
  if (value[0] == "[") {
    node.toggleAttribute(value.slice(1, -1))
  } else if (value[0] == ".") {
    node.classList.toggle(value.slice(1))
  }
}

function onShowClick (event) {
  const target = event.target.closest(SEL_SHOW)
  const sel = target.getAttribute(ATTR_SHOW_DIALOG) || ""
  for (const dialog of document.querySelectorAll(sel)) {
    dialog.showDialog()
  }
}

})()
