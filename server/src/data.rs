use crate::film_omdb;
use crate::get_movie_images;
use crate::load::load;
use crate::read_file;
use crate::HSHSS;

#[derive(Clone)]
pub struct Data {
    pub index_html: String,
    pub film_director: HSHSS,
    pub film_director_inverted: HSHSS,
    pub film_cast_member: HSHSS,
    pub film_cast_member_inverted: HSHSS,
    pub film_omdb: HSHSS,
    pub film_label: HSHSS,
    pub voice_actor_label_inverted: HSHSS,
    pub film_label_inverted: HSHSS,
    pub film_label_by_language: HSHSS,
    pub ids: Vec<String>,
    pub director_label_inverted: HSHSS,
    pub actor_label: HSHSS,
    pub actor_label_inverted: HSHSS,
    pub voice_actor_label_by_language: HSHSS,
    pub movie_images: HSHSS,
    pub voice_actor_label: HSHSS,
    pub film_voice_actor: HSHSS,
    pub film_voice_actor_inverted: HSHSS,
    pub composer_label: HSHSS,
    pub composer_label_inverted: HSHSS,
    pub film_composer: HSHSS,
    pub film_composer_inverted: HSHSS,
    pub film_imdb: HSHSS,
    pub director_label_by_language: HSHSS,
    pub actor_label_by_language: HSHSS,
    pub composer_label_by_language: HSHSS,

    pub film_main_subject_inverted: HSHSS,
    pub main_subject_label_inverted: HSHSS,
    pub film_genre_inverted: HSHSS,
    pub film_genre: HSHSS,
    pub genre_label_inverted: HSHSS,
    pub genre_label: HSHSS,
}

pub fn load_data() -> std::io::Result<Data> {
    let hs3_s = load();
    let ids: Vec<String> = hs3_s["film_label"]
        .clone()
        .keys()
        .map(std::clone::Clone::clone)
        .collect::<Vec<String>>();
    Ok(Data {
        index_html: read_file("../front/index.html")?,
        film_omdb: film_omdb(&hs3_s["film_imdb_inverted"])?,
        film_label: hs3_s["film_label"].clone(),
        ids,
        film_label_inverted: hs3_s["film_label_inverted"].clone(),
        film_label_by_language: hs3_s["film_label_by_language"].clone(),
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
        film_imdb: hs3_s["film_imdb"].clone(),
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
    })
}
