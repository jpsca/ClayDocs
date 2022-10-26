(function(){

const ATTR = 'data-toggle'
const SEL_TARGET = `[${ATTR}]`

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
  root.querySelectorAll(SEL_TARGET)
    .forEach( (node) => {
      node.addEventListener('click', onClick)
    })
}

addEvents(document)

function onClick (event) {
  const target = event.target.closest(SEL_TARGET)
  const [ sel, value ] = (target.getAttribute(ATTR) || "").split("|")
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

})()
