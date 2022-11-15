(function () {

  const SEL_DIALOG = ".SearchDialog"
  const SEL_INPUT = ".SearchInput"
  const SEL_RESULTS = ".SearchResults"
  const INDEX_ATTR = "data-index"

  // Minimum lenght of the search text
  // to start a search
  const MIN_INPUT_LENGTH = 3

  setupAll(document)

  function setupAll(root) {
    root.querySelectorAll(SEL_DIALOG)
      .forEach((dialog) => { setup(dialog) })
  }

  function setup(dialog) {
    const input = dialog.querySelector(SEL_INPUT)
    const results = dialog.querySelector(SEL_RESULTS)
    const resultTmpl = dialog.querySelector("template").innerHTML.trim()

    let idx, docs

    const indexUrl = input.getAttribute(INDEX_ATTR)
    fetch(indexUrl)
      .then((response) => response.json())
      .then((data) => {
        docs = data.docs
        idx = lunr.Index.load(data.index)
        input.addEventListener("input", onInput)
        dialog.showModal()
      })

    function onInput(event) {
      if (input.value.length >= MIN_INPUT_LENGTH) {
        const search_term = `${input.value}*`
        const matches = idx.search(search_term)
        showResults(matches)
      }
    }

    function showResults(matches) {
      results.textContent = ""
      const term = `<mark>${escapeReplacement(input.value)}</mark>`
      matches.forEach(function (match) {
        appendResult(match, term)
      })
    }

    function appendResult (match, term) {
      const page = docs[match.ref]
      const rx = new RegExp(escapeRegExp(input.value), "gi")
      const body = page.body.replace(rx, term)
      const title = page.title.replace(rx, term)

      const html = resultTmpl
        .replace("{URL}", match.ref)
        .replace("{TITLE}", title)
        .replace("{BODY}", body)
        .replace("{SCORE}", match.score)

      results.appendChild(htmlToElement(html))
    }

    /* UTILS */

    function escapeRegExp(string) {
      const escaped = string.replace(
        /[.+?^${}()|[\]\\]/g,
        "\\$&" // $& means the whole matched string
      )
      // Allow * to match anything in a word
      return escaped.replace(/\*/g, "\W*")
    }

    function escapeReplacement(string) {
      return string.replace(/\$/g, "$$$$").replace(/\*/g, "")
    }

    function htmlToElement(html) {
      var template = document.createElement("template");
      template.innerHTML = html;
      return template.content.firstChild;
    }
  }
})()
