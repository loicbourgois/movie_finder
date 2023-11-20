use crate::read_file;
use crate::HSHSHSS;

use std::collections::HashMap;

pub fn load() -> HSHSHSS {
    let mut hs3_s: HSHSHSS = HashMap::new();
    for k in [
        "actor_label",
        "actor_label_by_language",
        "actor_label_inverted",
        "cast_member_label",
        "cast_member_label_inverted",
        "composer_label",
        "composer_label_by_language",
        "composer_label_inverted",
        "director_label",
        "director_label_by_language",
        "director_label_inverted",
        "film_cast_member",
        "film_cast_member_inverted",
        "film_composer",
        "film_composer_inverted",
        "film_director",
        "film_director_inverted",
        "film_genre",
        "film_genre_by_language",
        "film_genre_inverted",
        "film_image",
        "film_image_inverted",
        "film_imdb",
        "film_imdb_inverted",
        "film_label",
        "film_label_2",
        "film_label_2_inverted",
        "film_label_by_language",
        "film_label_inverted",
        "film_main_subject",
        "film_main_subject_by_language",
        "film_main_subject_inverted",
        "film_omdb",
        "film_omdb_inverted",
        "film_publication",
        "film_publication_inverted",
        "film_screenwriter",
        "film_screenwriter_inverted",
        "film_voice_actor",
        "film_voice_actor_inverted",
        "genre_label",
        "genre_label_by_language",
        "genre_label_inverted",
        // "impawards",
        "main_subject_label",
        "main_subject_label_by_language",
        "main_subject_label_inverted",
        "screenwriter_label",
        "screenwriter_label_inverted",
        "television_series_label",
        "television_series_label_by_language",
        "television_series_label_inverted",
        "voice_actor_label",
        "voice_actor_label_by_language",
        "voice_actor_label_inverted",
    ] {
        hs3_s.insert(
            k.to_string(),
            serde_json::from_str(
                &read_file(&format!("../../movie_finder_local/data/map/{k}.json")).unwrap(),
            )
            .unwrap(),
        );
    }
    hs3_s
}
