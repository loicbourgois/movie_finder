#![feature(test)]

use movie_finder_database::count_per_language_1;
use movie_finder_database::count_per_language_2;
use movie_finder_database::database::Database;
use movie_finder_database::process_item;
use movie_finder_database::process_item_label;
use std::collections::HashMap;
extern crate test;
use test::Bencher;

fn get_db_small() -> Database {
    Database {
        item_id: HashMap::new(),
        item_kind: HashMap::new(),
        // item_label: HashMap::new(),
        label: Vec::new(),
        language_item_label: HashMap::new(),
        num_cpus: 10,
    }
}

fn get_db_big() -> Database {
    let mut db = get_db_small();
    process_item(&mut db);
    process_item_label(&mut db);
    db
}

#[bench]
fn b_count_per_language_1_small(b: &mut Bencher) {
    let db = get_db_small();
    b.iter(|| {
        count_per_language_1(&db);
    });
}

#[bench]
fn b_count_per_language_2_small(b: &mut Bencher) {
    let db = get_db_small();
    b.iter(|| {
        count_per_language_2(&db);
    });
}

#[bench]
fn b_count_per_language_1_big(b: &mut Bencher) {
    let db = get_db_big();
    b.iter(|| {
        count_per_language_1(&db);
    });
}

#[bench]
fn b_count_per_language_2_big(b: &mut Bencher) {
    let db = get_db_big();
    b.iter(|| {
        count_per_language_2(&db);
    });
}

#[test]
fn t_count_per_language_1() {
    let db = get_db_big();
    count_per_language_1(&db);
}
