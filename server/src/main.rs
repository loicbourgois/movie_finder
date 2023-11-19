use actix_cors::Cors;
use actix_web::http::header::ContentType;
use actix_web::{get, web, App, HttpResponse, HttpServer};
use openssl::ssl::{SslAcceptor, SslFiletype, SslMethod};
use rand::Rng;
use std::collections::HashMap;
use std::fs;

#[derive(serde::Serialize)]
struct Movie {
    id: String,
    omdb_id: HashMap<String, String>,
    directors: HashMap<String, Director>,
    cast_members: HashMap<String, CastMember>,
    voice_actors: HashMap<String, VoiceActor>,
    composers: HashMap<String, Composer>,
    titles: HashMap<String, String>,
    imdb: HashMap<String, String>,
    omdbs: HashMap<String, Omdb>,
    genres: HSHSS,
}

#[derive(Clone)]
struct Data {
    index_html: String,
    film_director: FilmDirector,
    film_director_inverted: FilmDirectorInverted,
    film_cast_member: FilmCastMember,
    film_cast_member_inverted: FilmCastMemberInverted,
    film_omdb: FilmOmdb,
    film_label: FilmLabel,
    voice_actor_label_inverted: HSHSS,
    film_label_inverted: FilmLabelInverted,
    film_label_by_language: HSHSS,
    ids: Vec<String>,
    director_label_inverted: HSHSS,
    actor_label: CastMemberLabel,
    actor_label_inverted: HSHSS,
    voice_actor_label_by_language: HSHSS,
    movie_images: OmdbMovieImages,
    voice_actor_label: HSHSS,
    film_voice_actor: HSHSS,
    film_voice_actor_inverted: HSHSS,
    composer_label: HSHSS,
    composer_label_inverted: HSHSS,
    film_composer: HSHSS,
    film_composer_inverted: HSHSS,
    film_imdb: HSHSS,
    director_label_by_language: HSHSS,
    actor_label_by_language: HSHSS,
    composer_label_by_language: HSHSS,

    film_main_subject_inverted: HSHSS,
    main_subject_label_inverted: HSHSS,
    film_genre_inverted: HSHSS,
    film_genre: HSHSS,
    genre_label_inverted: HSHSS,
    genre_label: HSHSS,
}

fn index_html(data: &web::Data<Data>) -> HttpResponse {
    HttpResponse::Ok()
        .content_type(ContentType::html())
        .body(data.index_html.to_string())
}

#[get("/")]
async fn index_html_1(data: web::Data<Data>) -> HttpResponse {
    index_html(&data)
}

#[get("/index.html")]
async fn index_html_2(data: web::Data<Data>) -> HttpResponse {
    index_html(&data)
}

fn movie_small(data: &web::Data<Data>, id: &str) -> MovieSmall {
    MovieSmall {
        id: id.to_string(),
        titles: match data.film_label_by_language.get(id) {
            None => HashMap::new(),
            Some(x) => x.clone(),
        },
        omdbs: match data.film_omdb.get(id) {
            Some(x) => {
                Some(x.iter()
                .filter(|(omdb_id, _)| data.movie_images.get(*omdb_id).is_some() )
                .map(|(omdb_id, _)| {
                    let (omdb_img_v, omdb_img_id) = data.movie_images[omdb_id].iter().next().unwrap();
                    (
                        omdb_id.clone(),
                        Omdb {
                            id: omdb_id.to_string(),
                            img_url: format!(
                                "https://www.omdb.org/image/default/{omdb_img_id}.jpeg?v={omdb_img_v}"
                            ),
                        },
                    )
                })
                .collect())
            }
            None => None
        }
    }
}

fn get_movie(id: &str, data: &web::Data<Data>) -> Movie {
    let omdb_ids = match data.film_omdb.get(id) {
        Some(x) => x.clone(),
        None => HashMap::new(),
    };
    Movie {
        id: id.to_string(),
        omdb_id: omdb_ids.clone(),
        titles: data.film_label_by_language[id].clone(),
        imdb: data.film_imdb[id].clone(),
        genres: match data.film_genre.get(id) {
            None => HashMap::new(),
            Some(x) => x
                .keys()
                .map(|id2| (id2.to_string(), data.genre_label[id2].clone()))
                .collect(),
        },
        omdbs: omdb_ids
            .keys()
            .filter(|omdb_id| data.movie_images.get(*omdb_id).is_some())
            .map(|omdb_id| {
                let (omdb_img_v, omdb_img_id) = data.movie_images[omdb_id].iter().next().unwrap();
                (
                    omdb_id.clone(),
                    Omdb {
                        id: omdb_id.to_string(),
                        img_url: format!(
                            "https://www.omdb.org/image/default/{omdb_img_id}.jpeg?v={omdb_img_v}"
                        ),
                    },
                )
            })
            .collect(),
        directors: match data.film_director.get(id) {
            None => HashMap::new(),
            Some(x) => x
                .keys()
                .map(|k| {
                    (
                        k.clone(),
                        Director {
                            id: k.to_string(),
                            names: data.director_label_by_language[k].clone(),
                            movies: data.film_director_inverted[k]
                                .keys()
                                .map(|k2| (k2.clone(), movie_small(data, k2)))
                                .collect(),
                        },
                    )
                })
                .collect(),
        },
        cast_members: match data.film_cast_member.get(id) {
            None => HashMap::new(),
            Some(x) => x
                .iter()
                .filter(|(k, __)| data.actor_label.get(*k).is_some())
                .map(|(k, _)| {
                    (
                        k.clone(),
                        CastMember {
                            id: k.to_string(),
                            names: data.actor_label_by_language[k].clone(),
                            movies: data.film_cast_member_inverted[k]
                                .keys()
                                .map(|k2| (k2.clone(), movie_small(data, k2)))
                                .collect(),
                        },
                    )
                })
                .collect(),
        },
        voice_actors: match data.film_voice_actor.get(id) {
            None => HashMap::new(),
            Some(x) => x
                .iter()
                .filter(|(k, __)| data.voice_actor_label.get(*k).is_some())
                .map(|(k, _)| {
                    (
                        k.clone(),
                        VoiceActor {
                            id: k.to_string(),
                            names: data.voice_actor_label_by_language[k].clone(),
                            movies: data.film_voice_actor_inverted[k]
                                .keys()
                                .map(|k2| (k2.clone(), movie_small(data, k2)))
                                .collect(),
                        },
                    )
                })
                .collect(),
        },
        composers: match data.film_composer.get(id) {
            None => HashMap::new(),
            Some(x) => x
                .iter()
                .filter(|(k, __)| data.composer_label.get(*k).is_some())
                .map(|(k, _)| {
                    (
                        k.clone(),
                        Composer {
                            id: k.to_string(),
                            names: data.composer_label_by_language[k].clone(),
                            movies: data.film_composer_inverted[k]
                                .keys()
                                .map(|k2| (k2.clone(), movie_small(data, k2)))
                                .collect(),
                        },
                    )
                })
                .collect(),
        },
    }
}

#[get("/random-movie")]
async fn random_movie(data: web::Data<Data>) -> HttpResponse {
    loop {
        let mut rng = rand::thread_rng();
        let idx = rng.gen_range(0..data.ids.len());
        let id = &data.ids[idx];
        if data.film_omdb.get(id).is_some() {
            return HttpResponse::Ok().json(get_movie(id, &data));
        }
    }
}

#[get("/get/{_id}")]
async fn get_item_html(_id: web::Path<String>, data: web::Data<Data>) -> HttpResponse {
    index_html(&data)
}

#[get("/get_json/{id}")]
async fn get_item_json(path: web::Path<String>, data: web::Data<Data>) -> HttpResponse {
    let id = path.into_inner();
    if data.film_label.get(&id).is_some() {
        HttpResponse::Ok().json(get_movie(&id, &data))
    } else {
        HttpResponse::Ok().into()
    }
}

#[get("/search/{_str}")]
async fn search_html(_str: web::Path<String>, data: web::Data<Data>) -> HttpResponse {
    index_html(&data)
}

fn search_by(
    search_str: &str,
    x_label_inverted: &HSHSS,
    film_x_inverted: &HSHSS,
    data: &web::Data<Data>,
) -> Vec<Vec<MovieSmall>> {
    let mut counter = 0;
    x_label_inverted
        .iter()
        .filter(|(k, _)| k.to_lowercase().contains(&search_str.to_lowercase()))
        .filter(|(_, _)| {
            counter += 1;
            counter <= 1000
        })
        .flat_map(|(_, v)| {
            v.keys()
                .filter(|k2| film_x_inverted.get(*k2).is_some())
                .map(|k2| {
                    film_x_inverted[k2]
                        .keys()
                        .map(|k3| movie_small(data, k3))
                        .collect::<Vec<_>>()
                })
                .collect::<Vec<_>>()
        })
        .collect()
}

#[get("/search_json/{search_path}")]
async fn search_json(search_path: web::Path<String>, data: web::Data<Data>) -> HttpResponse {
    println!("{search_path}");
    let search_str: String = search_path.into_inner();
    let mut counter = 0;
    let mut a: Vec<_> = data
        .film_label_inverted
        .iter()
        .filter(|(k, _)| k.to_lowercase().contains(&search_str.to_lowercase()))
        .filter(|(_, _)| {
            counter += 1;
            counter <= 1000
        })
        .map(|(_, v)| {
            v.keys()
                .map(|k2| movie_small(&data, k2))
                .collect::<Vec<_>>()
        })
        .collect();
    let mut results = Vec::new();
    results.append(&mut a);
    results.append(&mut search_by(
        &search_str,
        &data.director_label_inverted,
        &data.film_director_inverted,
        &data,
    ));
    results.append(&mut search_by(
        &search_str,
        &data.composer_label_inverted,
        &data.film_composer_inverted,
        &data,
    ));
    results.append(&mut search_by(
        &search_str,
        &data.actor_label_inverted,
        &data.film_cast_member_inverted,
        &data,
    ));
    results.append(&mut search_by(
        &search_str,
        &data.voice_actor_label_inverted,
        &data.film_voice_actor_inverted,
        &data,
    ));
    results.append(&mut search_by(
        &search_str,
        &data.main_subject_label_inverted,
        &data.film_main_subject_inverted,
        &data,
    ));
    results.append(&mut search_by(
        &search_str,
        &data.genre_label_inverted,
        &data.film_genre_inverted,
        &data,
    ));
    HttpResponse::Ok().json(results)
}

type FilmDirector = HashMap<String, HashMap<String, String>>;
type FilmOmdb = HashMap<String, HashMap<String, String>>;
type FilmDirectorInverted = HashMap<String, HashMap<String, String>>;
type FilmLabel = HashMap<String, HashMap<String, String>>;
type FilmLabelInverted = HashMap<String, HashMap<String, String>>;
type MovieID = String;
type OmdbMovieImages = HashMap<String, HashMap<String, String>>;
type FilmCastMember = HashMap<String, HashMap<String, String>>;
type FilmCastMemberInverted = HashMap<String, HashMap<String, String>>;
type CastMemberLabel = HashMap<String, HashMap<String, String>>;
type HSHSS = HashMap<String, HashMap<String, String>>;

#[derive(serde::Serialize, Debug)]
struct Omdb {
    id: String,
    img_url: String,
}

#[derive(serde::Serialize, Debug)]
struct MovieSmall {
    id: String,
    titles: HashMap<String, String>,
    omdbs: Option<HashMap<String, Omdb>>,
}

#[derive(serde::Serialize)]
struct Director {
    id: String,
    names: HashMap<String, String>,
    movies: HashMap<MovieID, MovieSmall>,
}

#[derive(serde::Serialize)]
struct CastMember {
    id: String,
    names: HashMap<String, String>,
    movies: HashMap<MovieID, MovieSmall>,
}

#[derive(serde::Serialize)]
struct VoiceActor {
    id: String,
    names: HashMap<String, String>,
    movies: HashMap<MovieID, MovieSmall>,
}

#[derive(serde::Serialize)]
struct Composer {
    id: String,
    names: HashMap<String, String>,
    movies: HashMap<MovieID, MovieSmall>,
}

fn get_movie_images() -> HSHSS {
    let mut rdr = csv::Reader::from_path("./omdb_images.csv").unwrap();
    let mut movie_images: OmdbMovieImages = HashMap::new();
    for result in rdr.records() {
        let record = result.unwrap();
        let image_id = &record[0];
        let object_id = &record[1];
        let object_type = &record[2];
        let image_version = &record[3];
        if object_type == "Movie" {
            match movie_images.get_mut(object_id) {
                Some(x) => {
                    x.insert(image_version.to_string(), image_id.to_string());
                }
                None => {
                    let mut aa = HashMap::new();
                    aa.insert(image_version.to_string(), image_id.to_string());
                    movie_images.insert(object_id.to_string(), aa);
                }
            }
        }
    }
    movie_images
}

fn film_omdb(film_imdb_inverted: &HSHSS) -> std::io::Result<HSHSS> {
    let mut film_omdb: HSHSS = serde_json::from_str(&read_file(
        "../../movie_finder_local/data/map/film_omdb.json",
    )?)?;

    let mut rdr = csv::Reader::from_path("./movie_links_imdb.csv").unwrap();
    for result in rdr.records() {
        let record = result.unwrap();
        let imdb = &record[1];
        let omdb = &record[2];
        match film_imdb_inverted.get(imdb) {
            Some(x) => {
                let wikidata = x.keys().next().unwrap();
                let mut hm = HashMap::new();
                hm.insert(omdb.to_string(), String::new());
                film_omdb.insert(wikidata.clone(), hm);
            }
            None => {}
        }
    }
    Ok(film_omdb)
}

fn read_file(path: &str) -> std::io::Result<String> {
    println!("reading {path}");
    fs::read_to_string(path)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    println!("main setup");
    let film_label: FilmLabel = serde_json::from_str(&read_file(
        "../../movie_finder_local/data/map/film_label.json",
    )?)?;
    let film_imdb = serde_json::from_str(&read_file(
        "../../movie_finder_local/data/map/film_imdb.json",
    )?)?;
    let film_imdb_inverted = serde_json::from_str(&read_file(
        "../../movie_finder_local/data/map/film_imdb_inverted.json",
    )?)?;
    let ids: Vec<String> = film_label
        .clone()
        .keys()
        .map(std::clone::Clone::clone)
        .collect::<Vec<String>>();
    let data = Data {
        index_html: read_file("../front/index.html")?,
        film_omdb: film_omdb(&film_imdb_inverted)?,
        film_label,
        ids,
        film_label_inverted: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/film_label_inverted.json",
        )?)?,
        film_label_by_language: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/film_label_by_language.json",
        )?)?,
        film_director: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/film_director.json",
        )?)?,
        film_director_inverted: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/film_director_inverted.json",
        )?)?,
        director_label_inverted: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/director_label_inverted.json",
        )?)?,
        film_cast_member: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/film_cast_member.json",
        )?)?,
        film_cast_member_inverted: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/film_cast_member_inverted.json",
        )?)?,
        actor_label: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/actor_label.json",
        )?)?,
        actor_label_inverted: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/actor_label_inverted.json",
        )?)?,

        voice_actor_label: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/voice_actor_label.json",
        )?)?,

        voice_actor_label_by_language: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/voice_actor_label_by_language.json",
        )?)?,

        director_label_by_language: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/director_label_by_language.json",
        )?)?,
        actor_label_by_language: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/actor_label_by_language.json",
        )?)?,
        composer_label_by_language: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/composer_label_by_language.json",
        )?)?,

        film_voice_actor: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/film_voice_actor.json",
        )?)?,
        film_voice_actor_inverted: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/film_voice_actor_inverted.json",
        )?)?,

        composer_label: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/composer_label.json",
        )?)?,
        composer_label_inverted: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/composer_label_inverted.json",
        )?)?,
        film_composer: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/film_composer.json",
        )?)?,
        film_composer_inverted: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/film_composer_inverted.json",
        )?)?,
        voice_actor_label_inverted: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/voice_actor_label_inverted.json",
        )?)?,
        film_imdb,
        movie_images: get_movie_images(),

        film_main_subject_inverted: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/film_main_subject_inverted.json",
        )?)?,
        main_subject_label_inverted: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/main_subject_label_inverted.json",
        )?)?,
        film_genre: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/film_genre.json",
        )?)?,
        film_genre_inverted: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/film_genre_inverted.json",
        )?)?,
        genre_label: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/genre_label.json",
        )?)?,
        genre_label_inverted: serde_json::from_str(&read_file(
            "../../movie_finder_local/data/map/genre_label_inverted.json",
        )?)?,
    };
    println!("main setup ok");
    let mut aa = HttpServer::new(move || {
        println!("setup");
        let cors = Cors::default()
            .allowed_origin("http://localhost")
            .allowed_origin("localhost")
            .allowed_origin("loicbourgois.com")
            .allowed_origin("http://loicbourgois.com")
            .allowed_origin("https://loicbourgois.com");
        let app = App::new()
            .app_data(web::Data::new(data.clone()))
            .wrap(cors)
            .service(index_html_1)
            .service(index_html_2)
            .service(random_movie)
            .service(get_item_html)
            .service(get_item_json)
            .service(search_html)
            .service(search_json)
            .service(actix_files::Files::new("/", "../front/"));
        println!("setup ok");
        app
    })
    .workers(1);
    let secure = true;
    if secure {
        let mut builder = SslAcceptor::mozilla_intermediate(SslMethod::tls()).unwrap();
        builder
            .set_private_key_file("/home/gravitle/privkey.pem", SslFiletype::PEM)
            .unwrap();
        builder
            .set_certificate_chain_file("/home/gravitle/fullchain.pem")
            .unwrap();
        aa = aa.bind_openssl("0.0.0.0:9000", builder)?;
    } else {
        aa = aa.bind(("0.0.0.0", 9000))?;
    }
    aa.run().await
}
