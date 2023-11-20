use crate::HSHSHSS;

use std::collections::HashMap;

pub fn search_media(
    search_str: &str,
    data_2: &HSHSHSS,
) -> HashMap<
    String,
    HashMap<String, Vec<String>>, // MediaSmall
> {
    let r1 = search(search_str, data_2);
    r1.values()
        .flat_map(|v| v.iter().map(std::string::ToString::to_string))
        .map(|x| (x.clone(), get_mappings(&x, data_2)))
        .collect::<HashMap<String, HashMap<String, Vec<String>>>>()
}

pub fn search(search_str: &str, data_2: &HSHSHSS) -> HashMap<String, Vec<String>> {
    data_2
        .keys()
        .filter(|key| key.contains("inverted/label/"))
        .collect::<Vec<_>>()
        .iter()
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

pub fn get_mappings(wikidata_id: &str, data_2: &HSHSHSS) -> HashMap<String, Vec<String>> {
    data_2
        .keys()
        .collect::<Vec<_>>()
        .iter()
        .map(|kind| {
            (
                (*kind).to_string(),
                data_2[&(*kind).to_string()]
                    .iter()
                    .filter(|(label, _)| label.to_lowercase().contains(&wikidata_id.to_lowercase()))
                    .flat_map(|(_, v)| v.keys().map(std::string::ToString::to_string))
                    .collect::<Vec<String>>(),
            )
        })
        .collect::<HashMap<String, Vec<String>>>()
}

// fn search_by(search_str: &str, x_label_inverted: &HSHSS, media_x_inverted: &HSHSS) -> Vec<String> {
//     let mut counter = 0;
//     x_label_inverted
//         .iter()
//         .filter(|(k, _)| k.to_lowercase().contains(&search_str.to_lowercase()))
//         .filter(|(_, _)| {
//             counter += 1;
//             counter <= 1000
//         })
//         .flat_map(|(_, v)| {
//             v.keys()
//                 .filter(|k2| media_x_inverted.get(*k2).is_some())
//                 .map(std::string::ToString::to_string)
//                 .collect::<Vec<_>>()
//         })
//         .collect()
// }
