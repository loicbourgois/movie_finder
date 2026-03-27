use movie_finder_database::count_per_language::count_per_language_1;
use movie_finder_database::count_per_language::count_per_language_2;
use movie_finder_database::count_title_contains::count_title_contains_1;
use movie_finder_database::count_title_contains::count_title_contains_2;
use movie_finder_database::count_title_contains::count_title_contains_3;
use movie_finder_database::count_title_contains::count_title_contains_4;
use movie_finder_database::count_title_contains::count_title_contains_5;
use movie_finder_database::count_title_contains::count_title_contains_6;
use movie_finder_database::count_title_contains::count_title_contains_7;
use movie_finder_database::count_title_lower_contains;
use movie_finder_database::database::Database;
use movie_finder_database::process_item;
use movie_finder_database::process_item_label;
use std::time::Instant;

fn timeit<F, R>(label: &str, func: F) -> R
where
    F: FnOnce() -> R,
{
    let start = Instant::now();
    let result = func();
    let duration = start.elapsed();
    println!("# {label}: {duration:?}");
    result
}

fn setup() -> Database {
    let mut database = Database::new();
    process_item(&mut database);
    process_item_label(&mut database);
    database
}

fn main() {
    let db = timeit("setup", setup);
    timeit("count_per_language_1", || count_per_language_1(&db));
    timeit("count_per_language_2", || count_per_language_2(&db));
    timeit("count_title_contains_1(Titanic)", || {
        count_title_contains_1(&db, "Titanic");
    });
    timeit("count_title_contains_2(Titanic)", || {
        count_title_contains_2(&db, "Titanic");
    });
    timeit("count_title_contains_3(Titanic)", || {
        count_title_contains_3(&db, "Titanic");
    });
    timeit("count_title_contains_4(Titanic)", || {
        count_title_contains_4(&db, "Titanic");
    });
    timeit("count_title_contains_5(Titanic)", || {
        count_title_contains_5(&db, "Titanic");
    });
    timeit("count_title_contains_6(Titanic)", || {
        count_title_contains_6(&db, "Titanic");
    });
    timeit("count_title_contains_7(Titanic)", || {
        count_title_contains_7(&db, "Titanic");
    });
    timeit("count_title_lower_contains(horizon)", || {
        count_title_lower_contains(&db, "horizon");
    });
}
