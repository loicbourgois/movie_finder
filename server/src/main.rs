// mod test;
use actix_web::http::header::ContentType;
use actix_web::{get, web, App, HttpResponse, HttpServer};
use rand::Rng;
use std::collections::HashMap;
use std::collections::HashSet;
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
    omdbs: HashMap<String, Omdb>,
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
    film_label_inverted: FilmLabelInverted,
    ids: Vec<String>,
    director_label: DirectorLabel,
    director_label_inverted: HSHSS,
    actor_label: CastMemberLabel,
    movie_images: OmdbMovieImages,

    voice_actor_label: HSHSS,
    film_voice_actor: HSHSS,
    film_voice_actor_inverted: HSHSS,

    composer_label: HSHSS,
    composer_label_inverted: HSHSS,
    film_composer: HSHSS,
    film_composer_inverted: HSHSS,
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
        titles: match data.film_label.get(id) {
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
    Movie {
        id: id.to_string(),
        omdb_id: data.film_omdb[id].clone(),
        titles: data.film_label[id].clone(),
        omdbs: data.film_omdb[id]
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
        directors: data.film_director[id]
            .keys()
            .map(|k| {
                (
                    k.clone(),
                    Director {
                        id: k.to_string(),
                        names: data.director_label[k].clone(),
                        movies: data.film_director_inverted[k]
                            .keys()
                            .map(|k2| (k2.clone(), movie_small(data, k2)))
                            .collect(),
                    },
                )
            })
            .collect(),
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
                            names: data.actor_label[k].clone(),
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
                            names: data.voice_actor_label[k].clone(),
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
                            names: data.composer_label[k].clone(),
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
    let mut b: Vec<Vec<MovieSmall>> = x_label_inverted
        .iter()
        .filter(|(k, v)| k.to_lowercase().contains(&search_str.to_lowercase()))
        .filter(|(_, _)| {
            counter += 1;
            counter <= 1000
        })
        .map(|(k, v)| {
            v.keys()
                .map(|k2| {
                    film_x_inverted[k2]
                        .keys()
                        .map(|k3| movie_small(&data, k3))
                        .collect::<Vec<_>>()
                })
                .flatten()
                .collect::<Vec<_>>()
        })
        .collect();
    return b;
}

#[get("/search_json/{search_path}")]
async fn search_json(search_path: web::Path<String>, data: web::Data<Data>) -> HttpResponse {
    println!("{search_path}");
    let search_str: String = search_path.into_inner();
    let mut counter = 0;
    let mut a: Vec<_> = data
        .film_label_inverted
        .iter()
        .filter(|(k, v)| k.to_lowercase().contains(&search_str.to_lowercase()))
        .filter(|(_, _)| {
            counter += 1;
            counter <= 1000
        })
        .map(|(k, v)| {
            v.keys()
                .map(|k2| movie_small(&data, k2))
                .collect::<Vec<_>>()
        })
        .collect();
    let mut uu = Vec::new();
    uu.append(&mut a);
    uu.append(&mut search_by(
        &search_str,
        &data.director_label_inverted,
        &data.film_director_inverted,
        &data,
    ));
    uu.append(&mut search_by(
        &search_str,
        &data.composer_label_inverted,
        &data.film_composer_inverted,
        &data,
    ));
    HttpResponse::Ok().json(uu)
}

type FilmDirector = HashMap<String, HashMap<String, String>>;
type FilmOmdb = HashMap<String, HashMap<String, String>>;
type FilmDirectorInverted = HashMap<String, HashMap<String, String>>;
type FilmLabel = HashMap<String, HashMap<String, String>>;
type FilmLabelInverted = HashMap<String, HashMap<String, String>>;
type DirectorLabel = HashMap<String, HashMap<String, String>>;
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

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let mut rdr = csv::Reader::from_path("./omdb_images.csv").unwrap();
    let mut object_types: HashSet<String> = HashSet::new();
    let mut movie_images: OmdbMovieImages = HashMap::new();
    for result in rdr.records() {
        let record = result.unwrap();
        let image_id = &record[0];
        let object_id = &record[1];
        let object_type = &record[2];
        let image_version = &record[3];
        object_types.insert(object_type.to_string());
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
    // println!("{:?}", object_types);
    // println!("{:?}", movie_images["24"]);
    println!("main setup");
    let film_label: FilmLabel = serde_json::from_str(&fs::read_to_string(
        "../../downtowhat_local/data/map/film_label.json",
    )?)?;
    let ids: Vec<String> = film_label
        .clone()
        .keys()
        .map(std::clone::Clone::clone)
        .collect::<Vec<String>>();
    let data = Data {
        index_html: fs::read_to_string("../front/index.html")?,
        film_omdb: serde_json::from_str(&fs::read_to_string(
            "../../downtowhat_local/data/map/film_omdb.json",
        )?)?,
        film_label,
        ids,
        film_label_inverted: serde_json::from_str(&fs::read_to_string(
            "../../downtowhat_local/data/map/film_label_inverted.json",
        )?)?,
        film_director: serde_json::from_str(&fs::read_to_string(
            "../../downtowhat_local/data/map/film_director.json",
        )?)?,
        film_director_inverted: serde_json::from_str(&fs::read_to_string(
            "../../downtowhat_local/data/map/film_director_inverted.json",
        )?)?,
        director_label: serde_json::from_str(&fs::read_to_string(
            "../../downtowhat_local/data/map/director_label.json",
        )?)?,
        director_label_inverted: serde_json::from_str(&fs::read_to_string(
            "../../downtowhat_local/data/map/director_label_inverted.json",
        )?)?,
        film_cast_member: serde_json::from_str(&fs::read_to_string(
            "../../downtowhat_local/data/map/film_cast_member.json",
        )?)?,
        film_cast_member_inverted: serde_json::from_str(&fs::read_to_string(
            "../../downtowhat_local/data/map/film_cast_member_inverted.json",
        )?)?,
        actor_label: serde_json::from_str(&fs::read_to_string(
            "../../downtowhat_local/data/map/actor_label.json",
        )?)?,

        voice_actor_label: serde_json::from_str(&fs::read_to_string(
            "../../downtowhat_local/data/map/voice_actor_label.json",
        )?)?,
        film_voice_actor: serde_json::from_str(&fs::read_to_string(
            "../../downtowhat_local/data/map/film_voice_actor.json",
        )?)?,
        film_voice_actor_inverted: serde_json::from_str(&fs::read_to_string(
            "../../downtowhat_local/data/map/film_voice_actor_inverted.json",
        )?)?,

        composer_label: serde_json::from_str(&fs::read_to_string(
            "../../downtowhat_local/data/map/composer_label.json",
        )?)?,
        composer_label_inverted: serde_json::from_str(&fs::read_to_string(
            "../../downtowhat_local/data/map/composer_label_inverted.json",
        )?)?,
        film_composer: serde_json::from_str(&fs::read_to_string(
            "../../downtowhat_local/data/map/film_composer.json",
        )?)?,
        film_composer_inverted: serde_json::from_str(&fs::read_to_string(
            "../../downtowhat_local/data/map/film_composer_inverted.json",
        )?)?,

        movie_images,
    };
    println!("main setup ok");
    HttpServer::new(move || {
        println!("setup");
        let app = App::new()
            .app_data(web::Data::new(data.clone()))
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
    .workers(1)
    .bind(("127.0.0.1", 8080))?
    .run()
    .await
}
