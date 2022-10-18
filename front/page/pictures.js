import * as header from '../components/header.js'
import * as http from '../http.js'
// import * as image_conversion from '../libs/image_conversion.js'

// import {compress, compressAccurately} from '../libs/image_conversion.js'


const upload = (image_id) => {


  // image_conversion.compressAccurately(file,{
  //   size: 100,    //The compressed image size is 100kb
  //   accuracy: 0.9,//the accuracy of image compression size,range 0.8-0.99,default 0.95;
  //                 //this means if the picture size is set to 1000Kb and the
  //                 //accuracy is 0.9, the image with the compression result
  //                 //of 900Kb-1100Kb is considered acceptable;
  //   type: "image/jpeg",
  //   width: 300,
  //   height: 200,
  //   orientation:2,
  //   scale: 0.5,
  // })


}


// function view(){
//   const file = document.getElementById('demo').files[0];
//   console.log(file);
//   imageConversion.compressAccurately(file,200).then(res=>{
//     //The res in the promise is a compressed Blob type (which can be treated as a File type) file;
//     console.log(res);
//   })
// }

// or use an async function
async function view() {
  const file = document.getElementById('demo').files[0];
  // console.log(document.getElementById('demo'))
  // console.log(file);
  // console.log(document.querySelector("#output_image").naturalWidth)
  const reader = new FileReader;
  reader.onload = function(evt) {
      var image = new Image();
      image.onload = async function(evt) {
          const file = document.getElementById('demo').files[0];
          document.querySelector("#input_image").src = URL.createObjectURL(file)
          document.querySelector("#input_image").width = this.width
          document.querySelector("#input_image").height = this.height
          const res = await imageConversion.compressAccurately(file,{
            size: 8,
            width: 512,
            height: 512,
          })
          document.querySelector("#output_image").src = URL.createObjectURL(res)
      };
      image.src = evt.target.result;
  };
  reader.readAsDataURL(file);
}

const choose_pic = () => {
  document.querySelector("#demo").click()
}



const go = async () => {
  window.upload = upload
  window.choose_pic = choose_pic
  window.view = view
  document.body.innerHTML = `
    ${await header.html()}
    <div id="pictures_content">
      <div id="picture_left">
        <img id="input_image">
      </div>
      <div id="picture_right">
        <img id="output_image" width="512" height="512">
        <div>
          <button onclick="choose_pic()">Choose a picture to upload</button>
          <input id="demo" type="file" onchange="view()">
        </div>
        <button onclick="upload(0)">Upload as image 1</button>
        <button onclick="upload(1)">Upload as image 2</button>
        <button onclick="upload(2)">Upload as image 3</button>
        <button onclick="upload(3)">Upload as image 4</button>
      </div>
    </div>
  `

  let aa = document.querySelector("#pictures_content").clientWidth-document.querySelector("#pictures_content").clientHeight
  // const aa = document.querySelector("#picture_right").clientWidth
  aa = Math.min(aa, 300)
  aa = 256
  document.querySelector("#picture_right img").style.height = aa + "px"
  document.querySelector("#picture_right img").style.width = aa + "px"
  document.querySelector("#picture_right").style.width = aa + "px"
  // console.log(document.querySelector("#picture_right img").width)
  // console.log(document.querySelector("#picture_right img").height)

  console.log(imageConversion.compressAccurately)



}


export {
  go
}
