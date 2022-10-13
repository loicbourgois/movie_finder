const base_url = "http://0.0.0.0"
let TOKEN = ""


const request = async(path, body_json) => {
  const options = {
    method: 'post',
    headers: {
      'Authorization': `Bearer ${TOKEN}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body_json)
  };
  const response = await fetch(`${base_url}/${path}`, options);
  return response;
}


const post = async(path, body_json) => {
  return await request(path, body_json).then( async (response) => {
    return await response.json()
  })
}


const login = async () => {
  TOKEN = (await post("/login", {
    'email': 'test@test.com',
    'password': 'hunter'
  })).token
}


import * as home from './page/home.js'


const go = (x) => {
  ({
    home: home.go
  }[x])()
}


const url_path = window.location.href.replace(window.location.origin+"/", '')
if (url_path.split("/")[0] == "") {
  go('home')
}


console.log(await post("/about") )
console.log(await post("/protected") )
console.log(await post("/protected") )
await login()
console.log(await post("/about") )
console.log(await post("/about") )
console.log(await post("/protected") )
console.log(await post("/protected") )
