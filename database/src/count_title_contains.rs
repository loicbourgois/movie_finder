use crate::Database;
use rayon::iter::IntoParallelRefIterator;
use rayon::iter::ParallelIterator;
use std::sync::Arc;
use std::sync::atomic::AtomicUsize;
use std::sync::atomic::Ordering;
use std::thread;

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
