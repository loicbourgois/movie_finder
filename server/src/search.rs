use crate::data_2::MediaSmall;
use crate::HSHSHSS;
use crate::HSHSS;
use std::collections::HashMap;

pub fn search_media(
    search_str: &str,
    data_2: &HSHSHSS,
    movie_images: &HSHSS,
) -> HashMap<String, MediaSmall> {
    let mut counter = 0;
    data_2
        .keys()
        .filter(|key| key.contains("inverted/label/"))
        .flat_map(|kind| {
            data_2[&(*kind).to_string()]
                .iter()
                .filter(|(label, _)| label.to_lowercase().contains(&search_str.to_lowercase()))
                .flat_map(|(_, v)| v.keys().map(std::string::ToString::to_string))
        })
        .filter(|_| {
            counter += 1;
            counter <= 1000
        })
        .map(|k| {
            let mut m = MediaSmall {
                wikidata_id: k.clone(),
                omdbs: HashMap::new(),
                titles: HashMap::new(),
            };
            get_mappings(&k, data_2)
                .iter()
                .map(|(k2, v2)| match k2.as_str() {
                    "base/relation/anime/omdb_id" | "base/relation/film/omdb_id" => {
                        for k3 in v2.keys() {
                            match movie_images.get(k3) {
                                Some(aa) => {
                                    match aa.iter().max_by_key(|(k, _v)| match k.parse::<i32>() {
                                        Ok(kv) => kv,
                                        Err(_) => {
                                            println!("{k}");
                                            0
                                        }
                                    }) {
                                        Some(v) => {
                                            m.omdbs.insert(v.1.to_string(), v.0.to_string());
                                        }
                                        None => {}
                                    }
                                }
                                None => {}
                            }
                        }
                    }
                    "by_language/label/film/film" | "by_language/label/anime/anime" => {
                        for (k3, v3) in v2 {
                            m.titles.insert(k3.to_string(), v3.to_string());
                        }
                    }
                    _ => {
                        if !v2.is_empty() {
                            println!("todo: {k2} {v2:?}");
                        }
                    }
                });
            (k, m)
        })
        .collect::<HashMap<String, MediaSmall>>()
}

pub fn search(search_str: &str, data_2: &HSHSHSS) -> HashMap<String, Vec<String>> {
    data_2
        .keys()
        .filter(|key| key.contains("inverted/label/"))
        .map(|kind| {
            (
                (*kind).to_string(),
                data_2[&(*kind).to_string()]
                    .iter()
                    .filter(|(label, _)| label.to_lowercase().contains(&search_str.to_lowercase()))
                    .flat_map(|(_, v)| v.keys().map(std::string::ToString::to_string))
                    .collect::<Vec<String>>(),
            )
        })
        .collect::<HashMap<String, Vec<String>>>()
}

pub fn get_mappings(
    wikidata_id: &str,
    data_2: &HSHSHSS,
) -> HashMap<String, HashMap<String, String>> {
    data_2
        .iter()
        .map(|(kind, _)| {
            (
                (*kind).to_string(),
                data_2[&(*kind).to_string()]
                    .iter()
                    .filter(|(k, _)| k.as_str() == wikidata_id)
                    .flat_map(|(_, v)| v.clone())
                    .collect::<HashMap<String, String>>(),
            )
        })
        .collect::<HashMap<String, HashMap<String, String>>>()
}
