const qa = sel => [...document.querySelectorAll(sel)]

function renderTex() {
  qa(".latex").map(el => {
    const options = {
      throwOnError: false
    }
    const html = katex.renderToString(el.innerHTML, options)
    el.innerHTML = html
  })
}

document.addEventListener('DOMContentLoaded', () => {
  renderTex()
})
