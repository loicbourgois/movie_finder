use crate::read_file;
use crate::HSHSHSS;
use std::collections::HashMap;
use std::collections::HashSet;

#[derive(serde::Serialize, Debug)]
pub struct MediaSmall {
    pub wikidata_id: String,
    pub titles: HashMap<String, String>,
    pub omdbs: HashMap<String, String>,
}

pub fn load_data_2() -> HSHSHSS {
    let mut hs3_s: HSHSHSS = HashMap::new();
    let mut keys: HashSet<String> = HashSet::new();
    for k in ["base/relation/anime/omdb_id", "base/relation/film/omdb_id"] {
        keys.insert(k.to_string());
    }
    for media in ["anime", "film"] {
        for language in ["fr", "ja", "en"] {
            for k in [
                &format!("inverted/label/{language}/{media}/{media}"),
                &format!("inverted/label/{language}/{media}/genre"),
                &format!("by_language/label/{language}/{media}/{media}"),
            ] {
                keys.insert(k.to_string());
            }
        }
        keys.insert(format!("inverted/relation/{media}/genre"));
    }
    for k in keys {
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
