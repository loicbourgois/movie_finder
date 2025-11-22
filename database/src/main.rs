mod kind_from_str;
mod kind;
use crate::kind_from_str::kind_from_str;
use crate::kind::Kind;
use std::path::PathBuf;
use csv::ReaderBuilder;
use std::collections::HashMap;


struct Item {
  item_id: usize,
  kind: Kind,
}


struct Database {
    item_id: HashMap<usize, usize>,
    item_kind: HashMap<usize, Kind>,
}


fn main() {
    println!("start");
    let home_dir = std::env::var("HOME").expect("HOME environment variable not set");
    let csv_path = PathBuf::from(home_dir.clone())
        .join("github.com/loicbourgois/movie_finder_local/data_v3/database/item.csv");
    let mut reader = ReaderBuilder::new()
        .has_headers(true)
        .flexible(true)
        .from_path(&csv_path).unwrap();
    let mut database = Database {
        item_id: HashMap::new(),
        item_kind: HashMap::new(),
    };
    for result in reader.records() {
        let record = result.unwrap();
        let item_id = record[0].parse().unwrap();
        database.item_id.insert(item_id, item_id);
        database.item_kind.insert(item_id, kind_from_str(&record[1]));
    }
}
