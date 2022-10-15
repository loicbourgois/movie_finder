import * as http from './http.js'


// const login = async () => {
//   const tokens = (await http.post("/login", {
//     'email': 'test@test.com',
//     'password': 'hunter'
//   }))
//   const secure = http.base_url.includes('https://') ? 'Secure' : ''
//   document.cookie = `access_token=${tokens.c}; SameSite=strict; ${secure}`
//   localStorage.setItem('access_token', tokens.a)
// }


import * as home from './page/home.js'
import * as play from './page/play.js'


const go = (x) => {
  ({
    home: home.go,
    play: play.go,
  }[x])()
}


const url_path = window.location.href.replace(window.location.origin+"/", '')
if (url_path.split("/")[0] == "") {
  go('home')
} else {
  go(url_path.split("/")[0])
}


// console.log(await http.post("/about") )
// console.log(await http.post("/protected") )
// console.log(await http.post("/protected") )
// await login()
// console.log(await http.post("/about") )
// console.log(await http.post("/about") )
// console.log(await http.post("/protected") )
// console.log(await http.post("/protected") )
