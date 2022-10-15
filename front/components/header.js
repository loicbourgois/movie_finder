window.header_login = () => {
  console.log("login")
}


window.header_join = () => {
  console.log("join")
}


const html = () => {
  return `
    <div id="header">
      <span id="title">Down to What</span>
      <span class="spacer"></span>
      <button id="button_login" onclick="header_login()">Login</button>
      <button onclick="header_join()">Register</button>
    </div>
  `
}


export {
  html,
}
