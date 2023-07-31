import * as http from './http.js'
import * as home from './page/home.js'
import * as play from './page/play.js'
import * as login from './page/login.js'
import * as pictures from './page/pictures.js'
import * as profile from './page/profile.js'


const go = (x) => {
  ({
    home: home.go,
    play: play.go,
    login: login.go,
    pictures: pictures.go,
    profile: profile.go,
  }[x])()
}


const url_path = window.location.href.replace(window.location.origin + "/", '')
if (url_path.split("/")[0] == "") {
  go('home')
} else {
  go(url_path.split("/")[0])
}