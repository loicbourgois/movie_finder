import * as header from '../components/header.js'
import * as http from '../http.js'
import * as login from './login.js'


const SQR = 2000
let source_image
let dest_image
let rdx = 0
let rdy = 0
let scale = 1.0


const load_file = () => {
  load_file_2(URL.createObjectURL(document.getElementById('demo').files[0]))
}


const test = () => {
  load_file_2("http://0.0.0.0/corgi_high.jpg")
}


const load_file_2 = (src) => {
  rdx = 0
  rdy = 0
  scale = 1.0
  var image = new Image();
  image.src = src;
  image.onload = function(){
    source_image = image
    process(source_image)
  }
}


const process = () => {
  document.querySelectorAll("button.picture_button").forEach((item, i) => {
    item.setAttribute('disabled', '');
  });
  crop_image(source_image)
  document.getElementById('canvas_cropped').toBlob((blob)=> {
    compress(blob)
  })
}


const crop_image = () => {
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = "#312";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  const canvas_cropped = document.getElementById('canvas_cropped');
  const ctx_cropped = canvas_cropped.getContext('2d');
  ctx_cropped.fillStyle = "#312";
  ctx_cropped.fillRect(0, 0, canvas_cropped.width, canvas_cropped.height);
  const image = source_image
  const r1 = Math.min(image.width / image.height, 1.0)
  const r2 = Math.min(image.height / image.width, 1.0)
  const r_square = Math.min(r1, r2) * scale
  ctx.drawImage(
    image,
    0,
    0,
    image.width,
    image.height,
    (SQR-SQR*r1)*0.5,
    (SQR-SQR*r2)*0.5,
    SQR*r1,
    SQR*r2,
  );
  ctx.lineWidth = 3
  ctx.strokeRect(
    (SQR-SQR*r_square)*0.5 + SQR * rdx,
    (SQR-SQR*r_square)*0.5 + SQR * rdy,
    SQR*r_square,
    SQR*r_square,
  );
  ctx_cropped.drawImage(image,
      ((image.width-image.width*r2)*0.5    + image.width*rdx / r1) + (1.0-scale)*image.width*0.5*r2,
      ((image.height-image.height*r1)*0.5  + image.height*rdy / r2) + (1.0-scale)*image.height*0.5*r1,
      image.width*r2*scale,
      image.height*r1*scale,
      0,
      0,
      SQR,
      SQR
  );
}


function blobToBase64_2(blob) {
  return new Promise((resolve, _) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result);
    reader.readAsDataURL(blob);
  });
}


const blobToBase64 = async (x) => {
  const aa = (await blobToBase64_2(x))
  return  aa.substr(aa.indexOf(',')+1)
}


const compress = (file) => {
  const reader = new FileReader;
  reader.onload = function(evt) {
      var image = new Image();
      image.onload = async function(evt) {
          const res = await imageConversion.compressAccurately(file, {
            size: 7.5,
            width: 512,
            height: 512,
          })
          document.querySelector("#output_image").src = URL.createObjectURL(res)
          dest_image = await blobToBase64(res)
          document.querySelectorAll("button.picture_button").forEach((item, i) => {
            item.removeAttribute('disabled');
          });
      };
      image.src = evt.target.result;
  };
  reader.readAsDataURL(file);
}


const choose_pic = () => {
  document.querySelector("#demo").click()
}


const zoom_in = () => {
  scale *= 0.9
  process()
}

const zoom_out = () => {
  scale /= 0.9
  process()
}

const left = () => {
  rdx -= 0.025*scale
  process()
}

const right = () => {
  rdx += 0.025*scale
  process()
}

const up = () => {
  rdy -= 0.025*scale
  process()
}

const down = () => {
  rdy += 0.025*scale
  process()
}


const upload = async (picture_id) => {
  const r = (await http.post("/add_picture", {
    'picture_id': picture_id,
    'data': dest_image,
  }))
  refresh_pictures()
}


const refresh_pictures = async () => {
  const promises = []
  for (var i of [0,1,2,3]) {
    promises.push(await http.post("/get_picture", {
      'picture_id': i,
    }))
  }
  for (var i of [0,1,2,3]) {
    const r = await promises[i]
    document.querySelector(`#picture_${i}`).src = 'data:image;base64,'+atob(r.data);
  }
}


const go = async () => {
  await login.do_login("test0@test.com", "hunter")
  window.choose_pic = choose_pic
  window.load_file = load_file
  window.zoom_in = zoom_in
  window.zoom_out = zoom_out
  window.up = up
  window.down = down
  window.left = left
  window.right = right
  window.upload = upload
  document.body.innerHTML = `
    ${await header.html()}
    <div id="pictures_content">

      <div id="picture_right">
        <canvas id="canvas_cropped" width="${SQR}" height="${SQR}"></canvas>
        <img id="output_image" width="512" height="512">
        <div>
          <button class="picture_button" onclick="choose_pic()">Choose a picture to upload</button>
          <input id="demo" type="file" onchange="load_file()">
        </div>
        <div>
          <button class="picture_button" onclick="up()">Up</button>
          <button class="picture_button" onclick="down()">Down</button>
          <button class="picture_button" onclick="left()">Left</button>
          <button class="picture_button" onclick="right()">Right</button>
        </div>
        <div>
          <button class="picture_button" onclick="zoom_in()">Zoom in</button>
          <button class="picture_button" onclick="zoom_out()">Zoom out</button>
        </div>
        <button class="picture_button" onclick="upload(0)">Upload as picture 1</button>
        <button class="picture_button" onclick="upload(1)">Upload as picture 2</button>
        <button class="picture_button" onclick="upload(2)">Upload as picture 3</button>
        <button class="picture_button" onclick="upload(3)">Upload as picture 4</button>
        <img class="picture" id="picture_0" width="512" height="512">
        <img class="picture" id="picture_1" width="512" height="512">
        <img class="picture" id="picture_2" width="512" height="512">
        <img class="picture" id="picture_3" width="512" height="512">
      </div>
      <canvas id="canvas" width="${SQR}" height="${SQR}"></canvas>
    </div>
  `
  const uu = Math.min(
    document.querySelector("#pictures_content").clientHeight,
    document.querySelector("#pictures_content").clientWidth - document.querySelector("#picture_right").clientWidth
  )
  document.querySelector("#canvas").style.height = uu + "px"
  document.querySelector("#canvas").style.width = uu + "px"
  test()
  refresh_pictures()
}


export {
  go
}
