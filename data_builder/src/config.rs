use serde::Deserialize;
use serde::Serialize;
// use std::collections::BTreeMap;
use std::collections::BTreeSet;
use std::collections::BTreeMap;
use std::fs;
use std::path::PathBuf;

#[derive(Debug, Deserialize)]
pub struct ConfigPython {
    pub data: BTreeMap<String, BTreeMap<String, BTreeMap<String, BTreeMap<u8, u8>>>>,
    pub omdb: BTreeMap<String, BTreeMap<u8, u8>>,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct Config {
    pub data: BTreeMap<String, BTreeMap<String, BTreeSet<String>>>,
    pub omdb: BTreeSet<String>,
}

fn transform(
    input: &BTreeMap<String, BTreeMap<String, BTreeMap<String, BTreeMap<u8, u8>>>>,
) -> BTreeMap<String, BTreeMap<String, BTreeSet<String>>> {
    let mut result = BTreeMap::new();
    for (outer_key, inner_map) in input {
        let mut level2_map = BTreeMap::new();
        for (inner_key, sub_map) in inner_map {
            let mut set = BTreeSet::new();
            for (sub_key, _deep_map) in sub_map {
                set.insert(sub_key.clone());
            }
            level2_map.insert(inner_key.clone(), set);
        }
        result.insert(outer_key.clone(), level2_map);
    }
    result
}

fn transform_2(
    input: &BTreeMap<String, BTreeMap<u8, u8>>,
) -> BTreeSet<String> {
            let mut set = BTreeSet::new();
            for (sub_key, _deep_map) in input {
                set.insert(sub_key.clone());
            }
    set
}

impl ConfigPython {
    pub fn to_config(&self) -> Config {
        Config {
            data: transform(&self.data),
            omdb: transform_2(&self.omdb),
        }
    }
}

pub fn get_config() -> Config {
    let home_dir = std::env::var("HOME").expect("HOME environment variable not set");
    let path = PathBuf::from(home_dir.clone())
        .join("github.com/loicbourgois/movie_finder/data_builder/config.json");
    let data = fs::read_to_string(&path)
        .unwrap_or_else(|e| panic!("Failed to read config file at {:?}: {}", path, e));
    let config_python: ConfigPython = serde_json::from_str(&data)
        .unwrap_or_else(|e| panic!("Failed to parse config JSON: {}", e));
    let config = config_python.to_config();
    let output_path = PathBuf::from(&home_dir)
        .join("github.com/loicbourgois/movie_finder/data_builder/config_rust.json");
    let serialized_config = serde_json::to_string_pretty(&config)
        .unwrap_or_else(|e| panic!("Failed to serialize config to JSON: {}", e));
    fs::write(&output_path, serialized_config)
        .unwrap_or_else(|e| panic!("Failed to write config to file at {:?}: {}", output_path, e));
    config
}
