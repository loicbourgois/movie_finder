use crate::data_2::MediaSmall;
use crate::HSHSHSS;
use crate::HSHSS;
use std::collections::HashMap;

#[derive(Debug)]
pub struct SourceItem<'a> {
    source: &'a String,
    wikidata_id: &'a String,
}

pub fn is_label(k: &str) -> bool {
    k.contains("by_language/label")
}

pub fn is_inverted(k: &str) -> bool {
    k.contains("inverted/")
}

pub fn search_media(
    search_str: &str,
    data_2: &HSHSHSS,
    movie_images: &HSHSS,
) -> HashMap<String, MediaSmall> {
    let mut counter = 0;
    // "inverted/relation/anime/genre"
    data_2
        .keys()
        .filter(|mapping_kind| mapping_kind.contains("inverted/label/fr/anime/genre"))
        .flat_map(|mapping_kind| {
            println!("mapping_kind: {mapping_kind}");
            data_2[&(*mapping_kind).to_string()]
                .iter()
                .filter(|(label, _)| label.to_lowercase().contains(&search_str.to_lowercase()))
                .flat_map(|(_, v)| {
                    v.keys().map(|k| SourceItem {
                        source: mapping_kind,
                        wikidata_id: k,
                    })
                })
        })
        .filter(|source_item: &SourceItem| {
            counter += 1;
            counter <= 1000
        })
        .map(|source_item: SourceItem| {
            let wikidata_id = source_item.wikidata_id;
            let mut m = MediaSmall {
                wikidata_id: wikidata_id.clone(),
                omdbs: HashMap::new(),
                titles: HashMap::new(),
            };
            for (msk, msv) in get_mappings(&wikidata_id, data_2) {
                let msk_str = msk.as_str();
                match msk_str {
                    msk_str if is_label(msk_str) => {
                        for (k3, v3) in msv {
                            m.titles.insert(k3.to_string(), v3.to_string());
                        }
                    }
                    "base/relation/anime/omdb_id" | "base/relation/film/omdb_id" => {
                        for k3 in msv.keys() {
                            match movie_images.get(k3) {
                                Some(imgs) => {
                                    for (version, image_id) in imgs {
                                        m.omdbs.insert(image_id.to_string(), version.to_string());
                                    }
                                }
                                None => {
                                    println!("no image for: wikidata_id={wikidata_id} k3={k3}");
                                }
                            }
                        }
                    }
                    msk_str if is_inverted(msk_str) => {
                        // pass
                    }
                    other => {
                        println!("no implemented: {other}");
                    }
                }
            }
            (wikidata_id.clone(), m)
        })
        .collect::<HashMap<String, MediaSmall>>()
}

// pub fn search(search_str: &str, data_2: &HSHSHSS) -> HashMap<String, Vec<String>> {
//     data_2
//         .keys()
//         .filter(|key| key.contains("inverted/label/"))
//         .map(|kind| {
//             (
//                 (*kind).to_string(),
//                 data_2[&(*kind).to_string()]
//                     .iter()
//                     .filter(|(label, _)| label.to_lowercase().contains(&search_str.to_lowercase()))
//                     .flat_map(|(_, v)| v.keys().map(std::string::ToString::to_string))
//                     .collect::<Vec<String>>(),
//             )
//         })
//         .collect::<HashMap<String, Vec<String>>>()
// }

pub fn get_mappings(
    wikidata_id: &str,
    data_2: &HSHSHSS,
) -> HashMap<String, HashMap<String, String>> {
    let r = data_2
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
        .collect::<HashMap<String, HashMap<String, String>>>();
    r
}
