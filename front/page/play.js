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
  show_new_question(side, tmp_user_id, await http.post("/get_tmp_question", {'user_id': tmp_user_id}))
}


const show_new_question = (side, tmp_id, question) => {
  let bl = `<button class="answer a" onclick="tmp_answer('${side}', '${tmp_id}', '${question.question_id}', '${question.option_a_id}', '${question.option_b_id}')">${question.option_a}</button>`
  let br = `<button class="answer b" onclick="tmp_answer('${side}', '${tmp_id}', '${question.question_id}', '${question.option_b_id}', '${question.option_a_id}')">${question.option_b}</button>`
  if (Math.random() > 0.5 ) {
    const _ = bl
    bl = br
    br = _
  }
  document.querySelector(`#${side}`).innerHTML = `
    <p class="prompt">${question.prompt}</p>
    <div class="answers">
      <span class="spacer"></span>
      ${bl}
      ${br}
      <span class="spacer"></span>
    </div>
  `
}


const assert = (x) => {
  if (!x) {
    throw 'Assert Error';
  }
}


const create_tmp_user = async () => {
  const tmp_user = await http.post("/create_tmp_user")
  localStorage.setItem('dtw.tmp_user_1.id', tmp_user.id)
}


const get_tmp_id_1 = async (retry_on_fail = true) => {
  try {
    const id = localStorage.getItem('dtw.tmp_user_1.id')
    assert(id)
    assert ( id == (await http.post("/get_tmp_user", {"user_id":id})).id )
    return id
  } catch (e) {
    if (retry_on_fail) {
      await create_tmp_user()
      return get_tmp_id_1(false)
    } else {
      throw e
    }
  }
}


const go = async () => {
  window.tmp_answer = tmp_answer
  document.body.innerHTML = `
    ${header.html()}
    <div id="play_content_wrapper">
      <div id="play_content">
        <div id="left"></div>
        <div id="right"></div>
      </div>
      <button class="button_less">Duo mode</button>
    </div>

  `
  const tmp_id_1 = await get_tmp_id_1()
  const question = await http.post("/get_tmp_question", {
    'user_id': tmp_id_1,
  })
  show_new_question('left', tmp_id_1, question)
}


export {
  go,
}
