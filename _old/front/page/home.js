import * as header from '../components/header.js'
import * as http from '../http.js'
import * as login from './login.js'


const play = () => {
  window.location = "/play"
}


const refresh_results = async () => {
  console.log("refresh")
  const r = await http.post("/get_matches", {
    filters: {
      last_active: document.querySelector("#last_active").value,
      min_match: document.querySelector("#min_match").value,
      max_distance: document.querySelector("#max_distance").value,
    }
  })
  console.log(r)
  let h = ""
  for (let x of Object.values(r)) {
    console.log(x.o_username)
    h += `
      <div class="profile">
        <div class="score_name">
          <span>${parseInt(x.m*100)}</span>
          <label>${x.o_username}</label>
        </div>
        <img src="corgi.jpg">
        <p class="o_description">${x.od}</p>
        <div class="pro_buttons">
          <button class="button_message">Message</button>
          <span class="spacer"></span>
          <button class="button_less">More</button>
          <span class="spacer"></span>
          <button class="button_less">Hide</button>
        </div>
      </div>
    `
  }
  document.querySelector("#results").innerHTML = h
}


const go = async () => {
  // await login.do_login("test0@test.com", "hunter")
  window.play = play
  window.refresh_results = refresh_results
  document.body.innerHTML = `
    <div id="filter"></div>
    ${await header.html()}
    <div id="content"></div>
  `
  if ( (await http.post("/protected") ).message == 'protected' ) {
    document.querySelector("#content").innerHTML = `
      <div id="home_logged_content">
        <div id="filters">
          <p>Show me people </p>
          <select name="last_active" id="last_active" onchange="refresh_results()">
            <option value="1_minute">Active less than a minute ago</option>
            <option value="1_hour">Active less than an hour ago</option>
            <option value="1_day">Active less than a day ago</option>
            <option value="1_week" selected>Active less than a week ago</option>
            <option value="1_month">Active less than a month ago</option>
          </select>
          <select name="min_match" id="min_match" onchange="refresh_results()">
            <option value="0.9">With 90+ compatibility</option>
            <option value="0.7">With 70+ compatibility</option>
            <option value="0.5">With 50+ compatibility</option>
            <option value="0.3">With 30+ compatibility</option>
            <option value="0.1">With 10+ compatibility</option>
            <option value="0"selected>With 0+ compatibility</option>
          </select>
          <select name="max_distance" id="max_distance" onchange="refresh_results()">
            <!-- <option value="5">5 km away or less</option>
            <option value="10">10 km away or less</option>
            <option value="25" selected>25 km away or less</option>
            <option value="50">50 km away or less</option>
            <option value="100">100 km away or less</option>
            <option value="250">250 km away or less</option>
            <option value="500">500 km away or less</option> -->
            <option value="any">Anywhere in the world</option>
          </select>
        </div>
        <div id="results"></div>
      </div>
    `
    refresh_results()
  } else {
    document.querySelector("#content").innerHTML = `
      <p id="p1">Answer questions, meet new people</p>
      <button id="letsgo_button" onclick="play()">ᐅ</button>
      <p id="letsgo_text">Let's go<span id="excla">!</span></p>
    `
  }
}


export {
  go,
}
