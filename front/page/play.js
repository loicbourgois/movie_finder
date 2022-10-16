import * as header from '../components/header.js'
import * as http from '../http.js'


const data = {}
let questions


const tmp_answer = async (side, tmp_user_id, question_id, winner_id, loser_id) => {
  await http.post("/tmp_answer", {
    'tmp_user_id': tmp_user_id,
    'question_id': question_id,
    'winner': winner_id,
    'loser': loser_id,
  })
  show_new_question(side, tmp_user_id, )
}


const tmp_reset = async (id) => {
  await http.post("/tmp_reset", {
    'tmp_user_id': id
  })
  refresh()
}


const show_new_question = async (side, tmp_id) => {
  if (get_mode() == 'duo') {
    const match_percent = await http.post("/tmp_match_percent", {
      'tmp_user_id_left': localStorage.getItem(`dtw.tmp_user.left.id`),
      'tmp_user_id_right': localStorage.getItem(`dtw.tmp_user.right.id`),
    })
    if (match_percent) {
      document.querySelector("#match").innerHTML = parseInt(match_percent*100)
    } else {
      document.querySelector("#match").innerHTML = "-"
    }
  }
  const progress = (await http.post("/tmp_progress", {
    'tmp_user_id': tmp_id,
  })).progress
  let question
  try {
    question = await http.post("/get_tmp_question", {'user_id': tmp_id})
    assert(question.question_id)
  } catch (e) {
    question={
      prompt: 'No more questions',
      option_a: '',
      option_b: '',
    }
  }
  let bl = `<button class="answer a" onclick="tmp_answer('${side}', '${tmp_id}', '${question.question_id}', '${question.option_a_id}', '${question.option_b_id}')">${question.option_a}</button>`
  let br = `<button class="answer b" onclick="tmp_answer('${side}', '${tmp_id}', '${question.question_id}', '${question.option_b_id}', '${question.option_a_id}')">${question.option_b}</button>`
  if (Math.random() > 0.5 ) {
    const _ = bl
    bl = br
    br = _
  }
  if (!question.question_id) {
    bl = ""
    br = ""
  }
  document.querySelector(`#${side}`).innerHTML = `
    <p class="prompt">${question.prompt}</p>
    <span class="spacer"></span>
    <div class="answers">
      <span class="spacer"></span>
      ${bl}
      ${br}
      <span class="spacer"></span>
    </div>
    <div id="progress_${side}" class="progress">
      <div id="progress_${side}_inner" class="progress_inner">
      </div>
    </div>
    <button class="button_less" onclick="tmp_reset('${tmp_id}')">Reset</button>
  `
  document.querySelector(`#progress_${side}_inner`).style.width = `${progress*100}%`
  try {
    if (get_mode() == 'duo') {
      document.querySelector(`#progress_left`).style.alignItems = `end`
    } else {
      document.querySelector(`#progress_left`).style.alignItems = `center`
    }
  } catch (e) {

  }
}


const assert = (x) => {
  if (!x) {
    throw 'Assert Error';
  }
}


const create_tmp_user = async (side) => {
  const tmp_user = await http.post("/create_tmp_user")
  localStorage.setItem(`dtw.tmp_user.${side}.id`, tmp_user.id)
}


const get_tmp_id = async (side, retry_on_fail = true) => {
  try {
    const id = localStorage.getItem(`dtw.tmp_user.${side}.id`)
    assert(id)
    assert ( id == (await http.post("/get_tmp_user", {"user_id":id})).id )
    return id
  } catch (e) {
    if (retry_on_fail) {
      await create_tmp_user(side)
      return get_tmp_id(side, false)
    } else {
      throw e
    }
  }
}


const solo = async () => {
  try {
    document.querySelector(`#progress_left`).style.alignItems = `center`
  } catch (e) {}
  document.querySelector("#solo_button").classList.add("display_none")
  document.querySelector("#center").classList.add("display_none")
  document.querySelector("#right").classList.add("display_none")
  show_new_question('left', await get_tmp_id('left'))
  document.querySelector("#duo_button").classList.remove("display_none")
  localStorage.setItem(`dtw.mode`, 'solo')
}


const duo = async () => {
  try {
    document.querySelector(`#progress_left`).style.alignItems = `end`
  } catch (e) {}
  document.querySelector("#duo_button").classList.add("display_none")
  const tmp_id_left = await get_tmp_id('left')
  const tmp_id_right = await get_tmp_id('right')
  show_new_question('left', tmp_id_left)
  show_new_question('right', tmp_id_right)
  document.querySelector("#solo_button").classList.remove("display_none")
  document.querySelector("#right").classList.remove("display_none")
  document.querySelector("#center").classList.remove("display_none")
  localStorage.setItem(`dtw.mode`, 'duo')
}


const get_mode = () => {
  return localStorage.getItem(`dtw.mode`)
}


const refresh = () => {
  if (get_mode() == 'duo') {
    duo()
  } else {
    solo()
  }
}


const go = async () => {
  window.tmp_answer = tmp_answer
  window.duo = duo
  window.solo = solo
  window.tmp_reset = tmp_reset
  document.body.innerHTML = `
    ${await header.html()}
    <div id="play_content_wrapper">
      <div id="play_content">
        <div id="left"></div>
        <div id="center">
          <p id="match">-</p>
        </div>
        <div id="right"></div>
      </div>
      <div class="spacer"></div>
      <button id="duo_button" class="button_less button_mode" onclick="duo()">Duo mode</button>
      <button id="solo_button" class="button_less button_mode" onclick="solo()">Solo mode</button>
    </div>
  `
  refresh()
}


export {
  go,
}
