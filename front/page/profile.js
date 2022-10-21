import * as header from '../components/header.js'
import * as http from '../http.js'
import * as login from './login.js'


const go = async () => {
  if ( (await http.post("/protected") ).message != 'protected' ) {
    window.location = "/login"
  }
  document.body.innerHTML = `
    ${await header.html()}
    <div id="profile_content">
      <a href="/pictures">Pictures</a>
    </div>
  `
}


export {
  go
}
