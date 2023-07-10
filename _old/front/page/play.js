import * as header from '../components/header.js'
import * as http from '../http.js'


const data = {}
let questions


const copy_to_clipboard = async (m) => {
  await copyToClipboard(m)
  alert(`${m} copied to clipboard`)
}


function copyToClipboard(textToCopy) {
    // navigator clipboard api needs a secure context (https)
    if (navigator.clipboard && window.isSecureContext) {
        // navigator clipboard api method'
        return navigator.clipboard.writeText(textToCopy);
    } else {
        // text area method
        let textArea = document.createElement("textarea");
        textArea.value = textToCopy;
        // make the textarea out of viewport
        textArea.style.position = "fixed";
        textArea.style.left = "-999999px";
        textArea.style.top = "-999999px";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        return new Promise((res, rej) => {
            // here the magic happens
            document.execCommand('copy') ? res() : rej();
            textArea.remove();
        });
    }
}


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


const change_alias = async (html_id, tmp_user_id) => {
  await http.post("/set_tmp_pseudo", {
    'pseudo': document.querySelector("#"+html_id).value,
    'tmp_user_id': tmp_user_id,
  })
  update_shared_match()
}


const show_new_question = async (side, tmp_id) => {
  const tmp_user = (await http.post("/get_tmp_user", {
    'tmp_user_id': tmp_id,
  }))
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
  const share_id = await http.post("/get_tmp_user_share_id", {
    'tmp_user_id': localStorage.getItem(`dtw.tmp_user.${side}.id`)
  })
  const link = `${window.location.origin}/play/${share_id.id}`
  let vis = "visibility: hidden;"
  const location_split = String(window.location).split('/')
  const last_part_location = location_split[location_split.length-1]
  if (last_part_location.length == 36) {
    vis = ""
  }
  let m = "-"
  try {
    m = document.querySelector(`#shared_match_wrapper_${side} .shared_match`).innerHTML
  } catch (e) { }

  let sma = "-"
  try {
    sma = document.querySelector(`#shared_match_wrapper_${side} .shared_match_alias`).innerHTML
  } catch (e) { }

  document.querySelector(`#${side}`).innerHTML = `
    <input id="alias_${side}" class="alias" placeholder="Alias" value="${tmp_user.pseudo}" onchange="change_alias('alias_${side}', '${tmp_user.id}')"></input>
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
    <div class="tmp_less_buttons">
      <button class="button_less" onclick="tmp_reset('${tmp_id}')">Reset answers</button>
      <button class="button_less"  onclick="copy_to_clipboard('${link}')">Copy sharing link</button>
    </div>
    <div id="shared_match_wrapper_${side}" class="shared_match_wrapper" style="${vis}">
      <p class="shared_match">${m}</p>
      <p class="shared_match_alias">${sma}</p>
    </div>
  `
  document.querySelector(`#progress_${side}_inner`).style.width = `${tmp_user.progress*100}%`
  try {
    if (get_mode() == 'duo') {
      document.querySelector(`#progress_left`).style.alignItems = `end`
    } else {
      document.querySelector(`#progress_left`).style.alignItems = `center`
    }
  } catch (e) {}
  update_shared_match()
  update_duo_match()
}


const update_duo_match = async () => {
  if (get_mode() == 'duo') {
    const r = await http.post("/tmp_match_percent", {
      'tmp_user_id_left': localStorage.getItem(`dtw.tmp_user.left.id`),
      'tmp_user_id_right': localStorage.getItem(`dtw.tmp_user.right.id`),
    })
    if (r && r.matching) {
      document.querySelector("#match").innerHTML = parseInt(r.matching*100)
    } else {
      document.querySelector("#match").innerHTML = "-"
    }
  }
}


const update_shared_match = async () => {
  const location_split = String(window.location).split('/')
  const last_part_location = location_split[location_split.length-1]
  if (last_part_location.length == 36) {
    let sides = ["left"]
    if (get_mode() == 'duo') {
      sides = ["left", "right"]
    }
    for (var side of sides) {
      const r = await http.post('/tmp_match_percent_by_share_id', {
        'tmp_user_id': localStorage.getItem(`dtw.tmp_user.${side}.id`),
        'tmp_user_share_id': last_part_location,
      })
      if (r) {
        if (!r.pseudo) {
          r.pseudo = "-"
        }
        r.matching = parseInt(r.matching*100)
        if (!r.matching) {
          r.matching = "-"
        }
        document.querySelector(`#shared_match_wrapper_${side} .shared_match`).innerHTML = r.matching
        document.querySelector(`#shared_match_wrapper_${side} .shared_match_alias`).innerHTML = r.pseudo
      } else {
        document.querySelector(`#shared_match_wrapper_${side} .shared_match`).innerHTML = "-"
      }
    }
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
    assert ( id == (await http.post("/get_tmp_user", {"tmp_user_id":id})).id )
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
  localStorage.setItem(`dtw.mode`, 'duo')
  document.querySelector("#duo_button").classList.add("display_none")
  const tmp_id_left = await get_tmp_id('left')
  const tmp_id_right = await get_tmp_id('right')
  show_new_question('left', tmp_id_left)
  show_new_question('right', tmp_id_right)
  document.querySelector("#solo_button").classList.remove("display_none")
  document.querySelector("#right").classList.remove("display_none")
  document.querySelector("#center").classList.remove("display_none")
}


const get_mode = () => {
  return localStorage.getItem(`dtw.mode`)
}


const refresh = async () => {
  if (get_mode() == 'duo') {
    await duo()
  } else {
    await solo()
  }
}


const go = async () => {
  window.tmp_answer = tmp_answer
  window.duo = duo
  window.solo = solo
  window.tmp_reset = tmp_reset
  window.copy_to_clipboard = copy_to_clipboard
  window.change_alias = change_alias
  document.body.innerHTML = `
    ${await header.html()}
    <div id="play_content_wrapper">
      <div id="play_content">
        <div id="left" class="play_side"></div>
        <div id="center">
          <p id="match">-</p>
        </div>
        <div id="right" class="play_side"></div>
      </div>
      <div class="spacer"></div>
      <button id="duo_button" class="button_less button_mode" onclick="duo()">Duo mode</button>
      <button id="solo_button" class="button_less button_mode" onclick="solo()">Solo mode</button>
    </div>
  `
  await refresh()
}


export {
  go,
}
