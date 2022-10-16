import * as http from '../http.js'


window.header_login = () => {
  console.log("login")
  window.location = "/login"
}


window.header_join = () => {
  console.log("join")
}


window.header_logout = () => {
  localStorage.setItem('access_token', "")
  window.location = ""
}


const html = async () => {
  if ( (await http.post("/protected") ).message == 'protected' ) {
    return `
      <div id="header">
        <a id="title" href="/">Down to What</a>
        <span class="spacer"></span>
        <button id="button_logout" onclick="header_logout()">Logout</button>
      </div>
    `
  } else {
    return `
      <div id="header">
        <a id="title" href="/">Down to What</a>
        <span class="spacer"></span>
        <button id="button_login" onclick="header_login()">Login</button>
        <button onclick="header_join()">Register</button>
      </div>
    `
  }
}


export {
  html,
}
