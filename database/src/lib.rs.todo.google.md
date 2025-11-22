```rust
pub mod database;
mod kind;
mod kind_from_str;
mod language;
mod language_from_str;
use crate::database::Database;
use crate::kind::Kind;
use crate::kind_from_str::kind_from_str;
use crate::language::Language;
use crate::language_from_str::language_from_str;
use csv::Reader;
use csv::ReaderBuilder;
use std::collections::BTreeMap;
use std::collections::HashMap;
use std::fs::File;
use std::path::PathBuf;

pub struct Label {
    pub language: Language,
    pub value: String,
}

fn get_path(path_str: &str) -> PathBuf {
    let home_dir = std::env::var("HOME").expect("HOME environment variable not set");
    PathBuf::from(path_str.replace("~", &home_dir))
}

fn csv_reader(path: &str) -> Reader<File> {
    ReaderBuilder::new()
        .has_headers(true)
        .flexible(true)
        .from_path(&get_path(path))
        .unwrap()
}

pub fn process_item(database: &mut Database) {
    for record_maybe in
        csv_reader("~/github.com/loicbourgois/movie_finder_local/data_v3/database/item.csv")
            .records()
    {
        let record = record_maybe.unwrap();
        let item_id = record[0].parse().unwrap();
        database.item_id.insert(item_id, item_id);
        database
            .item_kind
            .insert(item_id, kind_from_str(&record[1]));
    }
}

pub fn process_item_label(database: &mut Database) {
    for record_maybe in
        csv_reader("~/github.com/loicbourgois/movie_finder_local/data_v3/database/item___label.csv")
            .records()
    {
        let record = record_maybe.unwrap();
        let item_id: usize = record[0].parse().unwrap();
        let language = language_from_str(&record[1]);
        let label = &record[2];
        // database.item_label.insert(
        //     item_id,
        //     Label {
        //         language: language.clone(),
        //         value: label.to_string(),
        //     },
        // );
        database.label.push(label.to_string());
        let inner = database
            .language_item_label
            .entry(language)
            .or_insert_with(HashMap::new);
        inner.insert(item_id, label.to_string());
    }
}

pub fn count_per_language_1(database: &Database) {
    for (k, v) in &database.language_item_label {
        let aa: String = format!("{k:?}:");
        println!("{:<13} {}", aa, v.len());
    }
}

pub fn count_title_contains_1(db: &Database, value: &str) {
    let mut c = 0;
    for (k, v) in &db.language_item_label {
        for (k2, v2) in v {
            if v2.contains(value) {
                c += 1;
            }
        }
    }
    println!("{c}");
}

pub fn count_title_contains_2(db: &Database, value: &str) {
    let mut c = 0;
    for x in &db.label {
        if x.contains(value) {
            c += 1;
        }
    }
    println!("{c}");
}

// TODO: optimized version
// The original function signature `pub fn count_title_contains_23db: &Database, value: &str) {`
// contained a typo (`23db:` instead of `23db(` or a more meaningful name followed by `(`).
// This implementation provides an "optimized" version using Rust's iterator chain,
// which is often more idiomatic and can benefit from compiler optimizations.
// For extremely large datasets, parallel processing with `rayon` could be considered as a further optimization.
pub fn count_title_contains_optimized(db: &Database, value: &str) {
    let count = db.label.iter().filter(|label_text| label_text.contains(value)).count();
    println!("{count}");
}

pub fn count_per_language_2(database: &Database) {
    println!(
        "{:?}",
        database
            .language_item_label
            .iter()
            .map(|(k, v)| (k.clone(), v.len()))
            .collect::<BTreeMap<Language, usize>>()
    );
}

```