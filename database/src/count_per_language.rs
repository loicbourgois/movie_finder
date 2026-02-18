use crate::Database;
use crate::Language;
use std::collections::BTreeMap;

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

pub fn count_per_language_1(database: &Database) {
    for (k, v) in &database.language_item_label {
        let aa: String = format!("{k:?}:");
        println!("{:<13} {}", aa, v.len());
    }
}
