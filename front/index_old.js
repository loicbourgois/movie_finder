const LIMIT = 30000
let global_id = null
let maps = {}
const movie_small = (id) => {
    let year = null
    let search_query = first(maps.film_label[id])
    // if (maps.film_publication[id] && maps.film_publication[id][0] && maps.film_publication[id][0].split("-").length > 1) {
    //     year = maps.film_publication[id][0].split('-')[0]
    //     search_query = maps.film_label[id] + " " + year
    // }
    return {
        impawards: maps.impawards[id],
        id: id,
        title: first(maps.film_label[id]),
        year: year,
        search_query: search_query,
        imdb_id: keys(maps.film_imdb[id]),
        omdb_id: keys(maps.film_omdb[id]),
    }
}


const first = (a) => {
    let ks = keys(a)
    if (ks.length) {
        return ks[0]
    } else {
        return null
    }
} 


const keys = (a) => {
    if (a) {
        return Object.keys(a)
    } else {
        return []
    }
}

const values = (a) => {
    if (a) {
        return Object.values(a)
    } else {
        return []
    }
} 

const movie = (id) => {
    let m = {
        'id': id,
        'title': keys(maps.film_label[id]),
        'directors': keys(maps.film_director[id]),
        'cast_members': keys(maps.film_cast_member[id]),
        'screenwriters': keys(maps.film_screenwriter[id]),
        'voice_actors': keys(maps.film_voice_actor[id]),
        'impawards': keys(maps.impawards[id]),
        'related': {
            [id]: movie_small(id)
        }
    }
    for (const k of m.directors) {
        for (const movie_id of keys(maps.film_director_inverted[k])) {
            m.related[movie_id] = movie_small(movie_id)
        }
    }
    for (const k of m.cast_members) {
        for (const movie_id of keys(maps.film_cast_member_inverted[k])) {
            m.related[movie_id] = movie_small(movie_id)
        }
    }
    for (const k of m.voice_actors) {
        for (const movie_id of keys(maps.film_voice_actor_inverted[k])) {
            m.related[movie_id] = movie_small(movie_id)
        }
    }
    for (const k of m.screenwriters) {
        for (const movie_id of keys(maps.film_screenwriter_inverted[k])) {
            m.related[movie_id] = movie_small(movie_id)
        }
    }
    return m
}


const base_html = `
    <div id="header">
        <a id="random" href="/movie_front">Get lucky</a>
        <input id="search" placeholder="Search" onchange="trigger_search()"></input>
        <span id="infos">Loading...</span>
    </div>
    <div id="posters">
    </div>
    <div id="buttons">
    </div>
`


const show_movies = async (movies_, id) => {
    document.querySelector("body").innerHTML = base_html
    const l = Object.values(movies_).length
    let c = 0
    for (const k of Object.keys(movies_)) {
        const r = movies_[k]
        if (id != global_id) {
            return
        }
        if (c>=LIMIT){
            return
        }
        let picture_src = ``
        let imdb_link = ``
        // if (r.omdb_id) {
        //     for (const omdb_id of r.omdb_id) {
        //         const rr = await post("http://localhost:81/omdb", {
        //             'omdb_id': omdb_id
        //         })
        //         if (rr && rr.image_path) {
        //             picture_src = `../cache/${rr.image_path}`
        //             break
        //         }
        //     }
        // }
        // if (r.impawards && !picture_src ) {
        //     for (const url of r.impawards) {
        //         const rr = await post("http://localhost:81/impawards", {
        //             'url': url
        //         })
        //         if (rr.path) {
        //             picture_src = `../${rr.path}`
        //             break
        //         }
        //         if ( url.includes("/the_") ) {
        //             const r = await post("http://localhost:81/impawards", {
        //                 'url': url.replace("/the_", "/")
        //             })
        //             if (rr.path) {
        //                 picture_src = `../${rr.path}`
        //                 break
        //             }
        //         }
        //     }
        // }
        if (r.imdb_id) {
            for (const imdb_id of r.imdb_id) {
                imdb_link = `https://www.imdb.com/title/${imdb_id}/`
                // if (! picture_src) {
                //     const rr = await post("http://localhost:81/imdb", {
                //         'imdb_id': imdb_id
                //     })
                //     if (rr && rr.image_path) {
                //         picture_src = `../cache/${rr.image_path}`
                //         break
                //     }
                // }
            }
        }
        if (id != global_id) {
            return
        }
        if (c == 0) {
            document.querySelector("body").innerHTML = base_html
        }
        if (picture_src.length > 1) {
            document.querySelector("#posters").innerHTML += `
                <div class="movie">
                    <div class="movie_poster">
                        <img onclick="load_movie('${r.id}')" src="${picture_src}">
                    </div>
                    <div class="poster_links">
                        <a href="${imdb_link}">imdb</a>
                    </div>
                </div>
            `
        } else {
            document.querySelector("#buttons").innerHTML += `
            <div class="movie">
                <div>
                    <button onclick="load_movie('${r.id}')">${r.title}</button>
                </div>
            </div>
        `
        }
        c += 1
        document.querySelector("#infos").innerHTML = `${c} / ${Math.min(l, LIMIT)}`
    }
}


const load_movie = async (id) => {
    window.location.href = window.location.origin + window.location.pathname + "#" + id
    console.log(`loading movie ${id}`)
    global_id = id
    document.querySelector("body").innerHTML = base_html
    const m = movie(id)
    show_movies(m.related, id)
}


const post_inner = async(url, body_json) => {
    const options = {
      method: 'post',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body_json)
    };
    const response = await fetch(url, options);
    return response;
  }
  
  
const post = async(path, body_json) => {
    return await post_inner(path, body_json).then( async (response) => {
        return await response.json()
    })
}


const trigger_search = () => {
    search( document.querySelector("#search").value )
}


const search = (str_) => {
    console.log(`Searching ${str_}`)
    document.querySelector("#infos").innerHTML = "Searching..."
    global_id = str_
    let results = Object.entries(maps.film_label_inverted)
    for (const token of str_.split(" ") ) {
        const t = token.toLowerCase()
        results = results.filter ( ([k,v]) => {
            return k.toLowerCase().includes(t)
        } )
    }
    let r = {}
    for (const kv of results) {
        for (const id of keys(kv[1])) {
            r[id] = movie_small(id)
        }
    }
    let results_people = Object.entries(maps.actor_label_inverted)
    for (const token of str_.split(" ") ) {
        const t = token.toLowerCase()
        results_people = results_people.filter ( ([k,v]) => {
            return k.toLowerCase().includes(t)
        } )
    }
    for (const kv of results_people) {
        for (const id of keys(kv[1])) {
            for (const id2 of keys(maps.film_cast_member_inverted[id])  ) {
                r[id2] = movie_small(id2)
            }
        }
    }
    show_movies(r, str_)
    console.log(`Done searching`)
    document.querySelector("#infos").innerHTML = "Done searching"
}
  

const main = async () => {
    document.querySelector("body").innerHTML = base_html
    window.load_movie = load_movie
    window.trigger_search = trigger_search
    let requests = {}
    let responses = {}
    let jsons = {}
    let ks = [
        'film_director',
        'film_publication',
        'film_cast_member',
        'film_imdb',
        'film_omdb',
        'film_director_inverted',
        'film_cast_member_inverted',
        'film_voice_actor',
        'film_screenwriter',
        'film_voice_actor_inverted',
        'film_screenwriter_inverted',
        'actor_label_inverted',
        'impawards',
        'film_label',
        'film_label_inverted',
    ]
    for (const k of ks) {
        requests[k] = fetch(`/data/map/${k}.json`);
    }
    let l = ks.length
    let c = 0
    document.querySelector("#infos").innerHTML = `Fetching json ${c}/${l}`
    for (const k of ks) {
        responses[k] = await requests[k];
        c+=1
        document.querySelector("#infos").innerHTML = `Fetching json ${c}/${l}`
    }
     l = ks.length
     c = 0
     document.querySelector("#infos").innerHTML = `Loading json ${c}/${l}`
     for (const k of ks) {
        jsons[k] = responses[k].json();
        c+=1
        document.querySelector("#infos").innerHTML = `Loading json ${c}/${l}`
        console.log("aa")
    }
    c = 0
    document.querySelector("#infos").innerHTML = `Loading json ${c}/${l}`
    for (const k of ks) {
        maps[k] = await jsons[k];
        c+=1
        document.querySelector("#infos").innerHTML = `Loading json ${c}/${l}`
    }
    const wlhs = window.location.href.split('#')
    if (wlhs.length == 2) {
        load_movie(wlhs[1])
    } else {
        const movie_ids = Object.keys(maps.film_label)
        load_movie(movie_ids[parseInt(movie_ids.length * Math.random())])
    }
    // load_movie("Q165325")
    // search("samuel l jackson")
}
main()
