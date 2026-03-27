#![feature(test)]

mod common;

use movie_finder_database::count_per_language::count_per_language_1;
use movie_finder_database::count_per_language::count_per_language_2;
extern crate test;
use test::Bencher;

use crate::common::get_db_big;

// #[bench]
// fn b_count_per_language_1_small(b: &mut Bencher) {
//     let db = get_db_small();
//     b.iter(|| {
//         count_per_language_1(&db);
//     });
// }

// #[bench]
// fn b_count_per_language_2_small(b: &mut Bencher) {
//     let db = get_db_small();
//     b.iter(|| {
//         count_per_language_2(&db);
//     });
// }

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
