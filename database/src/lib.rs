pub mod count_per_language;
pub mod count_title_contains;
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
use std::fs::File;
use std::path::PathBuf;
use std::sync::Arc;
use std::sync::atomic::AtomicUsize;
use std::sync::atomic::Ordering;
use std::thread;

pub struct Label {
    pub language: Language,
    pub value: String,
}

fn get_path(path_str: &str) -> PathBuf {
    let home_dir = std::env::var("HOME").expect("HOME environment variable not set");
    PathBuf::from(path_str.replace('~', &home_dir))
}

fn csv_reader(path: &str) -> Reader<File> {
    ReaderBuilder::new()
        .has_headers(true)
        .flexible(true)
        .from_path(get_path(path))
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
        database.label_lower.push(label.to_lowercase().clone());
        let inner = database.language_item_label.entry(language).or_default();
        inner.insert(item_id, label.to_string());
    }
}

pub fn count_title_lower_contains(db: &Database, value_: &str) {
    let value_lower = value_.to_lowercase();
    let counter = Arc::new(AtomicUsize::new(0));
    let mut handles = vec![];
    let batch_size = 1000;
    let ptr = db.label_lower.as_ptr();
    for _ in 0..db.num_cpus {
        let counter = Arc::clone(&counter);
        let l = db.label_lower.len();
        unsafe {
            let slice = std::slice::from_raw_parts(ptr, l);
            let v = value_lower.clone();
            let handle = thread::spawn(move || {
                let mut c = 0;
                loop {
                    let idx = counter.fetch_add(batch_size, Ordering::Relaxed);
                    if idx > l {
                        break;
                    }
                    for label in slice.iter().take((idx + batch_size).min(l)).skip(idx) {
                        if label.contains(&v) {
                            c += 1;
                        }
                    }
                }
                c
            });
            handles.push(handle);
        }
    }
    let total: usize = handles.into_iter().map(|h| h.join().unwrap()).sum();
    println!("{total:?}");
}
