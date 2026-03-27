use movie_finder_database::database::Database;
use movie_finder_database::process_item;
use movie_finder_database::process_item_label;
use std::collections::HashMap;

pub fn get_db_small() -> Database {
    Database {
        item_id: HashMap::new(),
        item_kind: HashMap::new(),
        label: Vec::new(),
        label_lower: Vec::new(),
        language_item_label: HashMap::new(),
        num_cpus: 10,
    }
}

pub fn get_db_big() -> Database {
    let mut db = get_db_small();
    process_item(&mut db);
    process_item_label(&mut db);
    db
}
