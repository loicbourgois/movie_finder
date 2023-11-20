use crate::read_file;
use crate::HSHSHSS;
use std::collections::HashMap;

#[derive(serde::Serialize, Debug)]
struct MediaSmall {
    wikidata_id: String,
    titles: HashMap<String, String>,
    omdbs: HashMap<String, String>,
}

pub fn load_data_2() -> HSHSHSS {
    let mut hs3_s: HSHSHSS = HashMap::new();
    for k in [
        "base/label/anime/anime",
        "inverted/label/anime/anime",
        "inverted/label/film/film",
        "base/relation/anime/omdb_id",
        "base/relation/film/omdb_id",
    ] {
        hs3_s.insert(
            k.to_string(),
            serde_json::from_str(
                &read_file(&format!("../../movie_finder_local/data_v2/json/{k}.json")).unwrap(),
            )
            .unwrap(),
        );
    }
    hs3_s
}
