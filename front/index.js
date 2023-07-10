const base_html = `
    <div id="header">
        <a id="random" href="/movie_front">Get lucky</a>
        <input id="search" placeholder="Search" onchange="trigger_search()"></input>
        <span id="infos"></span>
    </div>
`

const get_inner = async(url) => {
    const response = await fetch(url, {
        method: 'get',
    });
    return response;
}
  
  
const get = async(path) => {
    return await get_inner(path).then( async (response) => {
        return await response.json()
    })
}


const omdb_url = (movie) => {
    let img_url = null
    let omdbs = []
    if (movie.omdbs) {
        omdbs = Object.values(movie.omdbs);
    }
    if (omdbs.length) {
        img_url = omdbs[0].img_url
    }
    return img_url
}


const show_movie = async (movie) => {
    document.querySelector("#infos").innerHTML = "Ready"
    let titles = Object.keys(movie.titles).join(" / ")
    document.querySelector("body").innerHTML += `
        <div>
            <h1>${titles}</h1>
            <div class="movies">
                <div class="movie">
                    <a class="movie_poster" href="${window.location.origin}/get/${movie.id}" >
                        <img src="${omdb_url(movie)}">
                    </a>
                </div>
            </div>
        </div>
    `
    for (const xx of [
        {
            'key': 'directors',
            'about': 'director',
        },
        {
            'key': 'composers',
            'about': 'composer',
        },
        {
            'key': 'cast_members',
            'about': 'cast member',
        },
        {
            'key': 'voice_actors',
            'about': 'voice actor',
        },
    ]) {
        Object.entries(movie[xx.key]).map((x)=> {
            const v = x[1]
            const names = Object.keys(v.names).join(' / ')
            const name_0 = Object.keys(v.names)[0]
            const movies = Object.entries(v.movies)
                .filter((x2) => {
                    return omdb_url(x2[1])
                })
                .map((x2) => {
                    return `
                    <div class="movie">
                        <a class="movie_poster" href="${window.location.origin}/get/${x2[1].id}" >
                            <img src="${omdb_url(x2[1])}">
                        </a>
                    </div>
                    `
                })
                .join("")
            document.querySelector("body").innerHTML += `
                <h2><a href="${window.location.origin}/search/${name_0}">${names} (${xx.about})</a></h2>
                <div class="movies">
                    ${movies}
                </div>
            `
        })
    }
}


const show_movies = async (moviess) => {
    let str_ =  `<div class="movies"></div><div class="movies">`
    const ids = {}
    for (const movies of moviess) {
        for (const movie of movies) {
            if (!omdb_url(movie)) {
                continue
            }
            if (ids[movie.id]) {
                continue
            }
            ids[movie.id] = true
            str_ += `
                <div class="movie">
                    <a class="movie_poster" href="${window.location.origin}/get/${movie.id}" >
                        <img src="${omdb_url(movie)}">
                    </a>
                </div>
            `
        }
    }
    str_ += `
        </div>
    `
    document.querySelector("body").innerHTML += str_
}


const show_random_movie = async () => {
    const r = await get("/random-movie")
    show_movie(r)
}


const trigger_search = () => {
    console.log(document.getElementById("search").value )
    window.location.href = window.location.origin + "/search/" + document.getElementById("search").value;
}


const main = async () => {
    document.querySelector("body").innerHTML = base_html
    document.trigger_search = trigger_search
    const wlhs = window.location.href.split('/')
    if (wlhs.length == 5) {
        if (wlhs[3] == "get") {
            const r = await get(`/get_json/${wlhs[4]}`)
            show_movie(r)
        }
        else if (wlhs[3] == "search") {
            const r = await get(`/search_json/${wlhs[4]}`)
            show_movies(r)
        }
    } else {
        show_random_movie()
    }
}
main()
