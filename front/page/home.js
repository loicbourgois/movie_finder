import * as header from '../components/header.js'
import * as http from '../http.js'


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
}


const go = async () => {
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
          <select name="last_active" id="last_active">
            <option value="1_hour">Active in the last minute</option>
            <option value="1_hour">Active in the last hour</option>
            <option value="1_day">Active in the last day</option>
            <option value="1_week" selected>Active in the last week</option>
            <option value="1_month">Active in the last month</option>
          </select>
          <select name="min_match" id="min_match">
            <option value="90">With 90+ compatibility</option>
            <option value="70">With 70+ compatibility</option>
            <option value="50">With 50+ compatibility</option>
            <option value="30">With 30+ compatibility</option>
            <option value="10"selected>With 10+ compatibility</option>
          </select>
          <select name="max_distance" id="max_distance">
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
