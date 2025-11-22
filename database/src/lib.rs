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
use rayon::prelude::*;
use std::collections::BTreeMap;
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
        database.label_lower.push(label.to_lowercase().to_string());
        let inner = database.language_item_label.entry(language).or_default();
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
    for v in db.language_item_label.values() {
        for v2 in v.values() {
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

pub fn count_title_contains_3(db: &Database, value: &str) {
    let count = db
        .label
        .iter()
        .filter(|label_text| label_text.contains(value))
        .count();
    println!("{count}");
}

pub fn count_title_contains_4(db: &Database, value: &str) {
    let count = db
        .label
        .par_iter()
        .filter(|label_text| label_text.contains(value))
        .count();
    println!("{count}");
}

pub fn count_title_contains_5(db: &Database, value: &str) {
    let mut handles = Vec::new();
    let ptr = db.label.as_ptr();
    let l = db.label.len();
    let step_size = l / (db.num_cpus - 2);
    for i in (0..l).step_by(step_size) {
        let start = i;
        let end = (start + step_size).min(l);
        let value = value.to_owned();
        unsafe {
            let slice = std::slice::from_raw_parts(ptr.add(start), end - start);
            handles.push(thread::spawn(move || {
                slice
                    .iter()
                    .filter(|label_text| label_text.contains(&value))
                    .count()
            }));
        }
    }
    let total: usize = handles.into_iter().map(|h| h.join().unwrap()).sum();
    println!("{total}");
}

pub fn count_title_contains_6(db: &Database, value: &str) {
    let ptr = db.label.as_ptr();
    let len = db.label.len();
    let threads = db.num_cpus.max(1);
    let chunk_size = len.div_ceil(threads);
    let mut handles = Vec::with_capacity(threads);
    let value = value.as_bytes();
    for chunk_start in (0..len).step_by(chunk_size) {
        let chunk_end = (chunk_start + chunk_size).min(len);
        let count = chunk_end - chunk_start;
        let value_ref = value.to_owned();
        unsafe {
            let slice = std::slice::from_raw_parts(ptr.add(chunk_start), count);
            handles.push(thread::spawn(move || {
                slice
                    .iter()
                    .filter(|label| label.contains(std::str::from_utf8(&value_ref).unwrap()))
                    .count()
            }));
        }
    }
    let total: usize = handles.into_iter().map(|h| h.join().unwrap()).sum();
    println!("{total}");
}

pub fn count_title_contains_7(db: &Database, value: &str) {
    let counter = Arc::new(AtomicUsize::new(0));
    let mut handles = vec![];
    let batch_size = 1000;
    let ptr = db.label.as_ptr();
    for _ in 0..db.num_cpus {
        let counter = Arc::clone(&counter);
        let l = db.label.len();
        unsafe {
            let slice = std::slice::from_raw_parts(ptr, l);
            let v = value.to_owned();
            let handle = thread::spawn(move || {
                let mut c = 0;
                loop {
                    let idx = counter.fetch_add(batch_size, Ordering::Relaxed);
                    if idx > l {
                        break;
                    }
                    for label in slice.iter().take((idx + batch_size).min(l)).skip(idx) {
                        // for i in idx..(idx + batch_size).min(l) {
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
            let v = value_lower.to_owned();
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
