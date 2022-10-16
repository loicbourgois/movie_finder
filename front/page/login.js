import * as header from '../components/header.js'
import * as http from '../http.js'


const login = async () => {
  document.querySelector("#info").innerHTML = ''
  try {
    const email = document.querySelector("#email").value
    const password = document.querySelector("#password").value
    const tokens = (await http.post("/login", {
      'email': email,
      'password': password,
    }))
    const secure = http.base_url.includes('https://') ? 'Secure' : ''
    document.cookie = `access_token=${tokens.c}; SameSite=strict; ${secure}`
    localStorage.setItem('access_token', tokens.a)
    window.location = "/"
  } catch (e) {
      document.querySelector("#info").innerHTML = `
        <p> Login failed </p>
      `
  }
}


const go = async () => {
  window.login = login
  document.body.innerHTML = `
    ${await header.html()}
    <div id="login_content">
      <input id="email" type="email" placeholder="email"></input>
      <input id="password" type="password" placeholder="password"></input>
      <div id="info"></div>
      <button onclick="login()">Login</button>
    </div>
  `
}


export {
  go
}
