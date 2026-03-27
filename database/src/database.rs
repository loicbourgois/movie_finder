use crate::Kind;
use crate::Language;
use num_cpus;
use std::collections::HashMap;

pub struct Database {
    pub item_id: HashMap<usize, usize>,
    pub item_kind: HashMap<usize, Kind>,
    // pub item_label: HashMap<usize, Label>,
    // pub item_language_label: HashMap<usize, HashMap<Language, String>>,
    pub language_item_label: HashMap<Language, HashMap<usize, String>>,
    pub label: Vec<String>,
    pub label_lower: Vec<String>,
    pub num_cpus: usize,
}

impl Default for Database {
    fn default() -> Self {
        Self::new()
    }
}

impl Database {
    #[must_use]
    pub fn new() -> Self {
        Self {
            item_id: HashMap::new(),
            item_kind: HashMap::new(),
            // item_label: HashMap::new(),
            language_item_label: HashMap::new(),
            label: Vec::new(),
            label_lower: Vec::new(),
            num_cpus: num_cpus::get(),
        }
    }
}
