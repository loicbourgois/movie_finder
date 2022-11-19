let film_label
let film_label_inverted
let film_director
let film_cast_member
let film_director_inverted
let film_cast_member_inverted
let impawards
const search = () => {
    // const r = Object.entries(film_label_inverted)
    //     .filter( ([key, value]) => key.toLowerCase().includes('big short') )
    //     .map( ([k, v]) => [v[0], {
    //         'title': k,
    //         'director': film_director[v[0]],
    //     }] )
//.filter( ([key, value]) => key.toLowerCase().includes('big short') )
}
const movie = (id) => {
    let m = {
        'id': id,
        'title': film_label[id],
        'directors': film_director[id],
        'cast_members': film_cast_member[id],
        'impawards': impawards[id],
        'related': {}
    }
    for (const k of m.directors) {
        if (film_director_inverted[k]) {
            for (const movie_id of film_director_inverted[k]) {
                m.related[movie_id] = {
                    impawards: impawards[movie_id],
                    id: movie_id,
                    title: film_label[movie_id],
                }
            }
        }
    }
    for (const k of m.cast_members) {
        if (film_cast_member_inverted[k]) {
            for (const movie_id of film_cast_member_inverted[k]) {
                m.related[movie_id] = {
                    impawards: impawards[movie_id],
                    id: movie_id,
                    title: film_label[movie_id],
                }
            }
        }
    }
    return m
}


const load_movie = (id) => {
    document.querySelector("body").innerHTML = ""
    const m = movie(id)
    for (const r of Object.values(m.related)) {
        let pictures = ``
        if (r.impawards) {
            for (const url of r.impawards) {
                pictures += `<img src="${url}">`
            }
        }
        document.querySelector("body").innerHTML += `
            <div>
                ${pictures}
                <button onclick="load_movie('${r.id}')">${r.title}</button>
            </div>
        `
    }
}


const main = async () => {
    // const aa = await fetch('https://upload.wikimedia.org/wikipedia/en/2/2c/Kill_Bill_Volume_1.png')
    // console.log(aa)
    // window.load_movie = load_movie
    // console.log("loading")
    // film_label = await (await fetch('/data/map/film_label.json')).json()
    // film_label_inverted = await (await fetch('/data/map/film_label_inverted.json')).json()
    // film_director = await (await fetch('/data/map/film_director.json')).json()
    // film_cast_member = await (await fetch('/data/map/film_cast_member.json')).json()
    // film_director_inverted = await (await fetch('/data/map/film_director_inverted.json')).json()
    // film_cast_member_inverted = await (await fetch('/data/map/film_cast_member_inverted.json')).json()
    // impawards = await (await fetch('/data/map/impawards.json')).json()
    // console.log("start")
    // load_movie("Q19850715")
    // const id = "Q19850715"
    // const q = fetch(`http://www.wikidata.org/w/api.php?action=wbgetentities&format=xml&props=sitelinks&ids=${id}&sitefilter=enwiki`)
    // const r = await q
    // document.body.innerHTML = "<iframe src='https://www.imdb.com/title/tt0378194/'>"
}
main()