(function () {

  const SEL_DIALOG = ".SearchDialog"
  const SEL_INPUT = ".SearchInput"
  const SEL_RESULTS = ".SearchResults"
  const INDEX_ATTR = "data-index"

  const MIN_WORD_LENGTH = 2

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

    function onInput (event) {
      let search_term = input.value.replace(/\s+/g, " ").trim()
      if (!search_term) { return }
      // search_term = search_term.split(" ").map(function (word) {
      //   return word.includes('*') ? word : word + "*"
      // }).join(" ")
      const matches =  idx.search(search_term)
      showResults(matches, search_term)
    }

    function showResults (matches, search_term) {
      results.textContent = ""
      matches.forEach(function (match) {
        appendResult(match, search_term)
      })
    }

    function appendResult (match, search_term) {
      const page = docs[match.ref]
      let body = page.body
      let title = page.title

      search_term.split(" ").forEach(function (word) {
        const rx = new RegExp(escapeRegExp(word), "gi")
        body = page.body.replace(rx, "<mark>$1</mark>")
        title = page.title.replace(rx, "<mark>$1</mark>")
      })

      const html = resultTmpl
        .replace("{URL}", page.loc)
        .replace("{PARENT}", page.parent || "")
        .replace("{TITLE}", title)
        .replace("{BODY}", body)
        .replace("{SCORE}", match.score)

      results.appendChild(htmlToElement(html))
    }

    /* UTILS */

    function escapeRegExp(word) {
      const escaped = word.replace(
        /[.+?^${}()|[\]\\]/g,
        "\\$&" // $& means the matched char
      )
      // Allow * to match anything in a word
      console.debug(escaped.replace(/\*/g, "\\W*"))
      return escaped.replace(/\*/g, "\\W*")
    }

    function htmlToElement(html) {
      var template = document.createElement("template");
      template.innerHTML = html;
      return template.content.firstChild;
    }
  }
})()
