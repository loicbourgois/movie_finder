import * as header from '../components/header.js'


const play = () => {
  window.location = "/play"
}


const go = () => {
  window.play = play
  document.body.innerHTML = `
    <div id="filter"></div>
    ${header.html()}
    <div id="content">
      <p id="p1">Answer questions, meet new people</p>
      <button id="letsgo_button" onclick="play()">ᐅ</button>
      <p id="letsgo_text">Let's go<span id="excla">!</span></p>
    </div>
  `
}


export {
  go,
}
// ᐊ
