#![feature(test)]
mod common;
use crate::common::get_db_big;
extern crate test;
use test::Bencher;
// use movie_finder_database::count_title_contains::count_title_contains_1;
// use movie_finder_database::count_title_contains::count_title_contains_2;
// use movie_finder_database::count_title_contains::count_title_contains_3;
use movie_finder_database::count_title_contains::count_title_contains_4;
// use movie_finder_database::count_title_contains::count_title_contains_5;
// use movie_finder_database::count_title_contains::count_title_contains_6;
use movie_finder_database::count_title_contains::count_title_contains_7;

#[bench]
fn b_count_title_contains_4(b: &mut Bencher) {
    let db = get_db_big();
    b.iter(|| {
        count_title_contains_4(&db, "Titanic");
    });
}

#[bench]
fn b_count_title_contains_7(b: &mut Bencher) {
    let db = get_db_big();
    b.iter(|| {
        count_title_contains_7(&db, "Titanic");
    });
}
