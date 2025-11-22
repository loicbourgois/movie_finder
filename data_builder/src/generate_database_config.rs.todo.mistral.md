I'll address the TODO by translating the Python `add_omdb()` function to Rust. Here's the implementation:

```rust
use std::fs::File;
use std::io::{BufRead, BufReader};
use csv::ReaderBuilder;
use std::path::Path;

fn column_type_sql(column_name: &str, _source: &str) -> &'static str {
    match column_name {
        "imdbID" | "imdbVotes" | "year" | "metascore" | "imdbRating" => "text",
        _ => "text", // Default to text for all other columns
    }
}

fn nullability_sql(_column_name: &str, _source: &str) -> &'static str {
    "null" // All columns are nullable in this case
}

fn add_omdb(config: &Config) -> (Vec<String>, BTreeMap<String, String>) {
    let mut create_tables = Vec::new();
    let mut table_names = BTreeMap::new();

    if let Some(omdb_config) = config.omdb.as_ref() {
        for name in omdb_config.keys() {
            let short_path = format!("omdb/{}", name);
            let table = format!("omdb___{}", name);
            let path = format!("/root/github.com/loicbourgois/movie_finder_local/data_v3/csv/{}.csv", short_path);

            // Read CSV file
            let file = File::open(&path).expect("Failed to open CSV file");
            let reader = BufReader::new(file);
            let mut rdr = ReaderBuilder::new()
                .has_headers(true)
                .from_reader(reader);

            // Get headers
            let headers = rdr.headers().expect("Failed to read headers").clone();

            // Process each column
            let mut columns_list = Vec::new();
            for column_name in headers.iter() {
                let column_type = column_type_sql(column_name, "omdb");
                let nullability = nullability_sql(column_name, "omdb");
                columns_list.push(format!("    {} {} {}", column_name, column_type, nullability));
            }

            // Create table SQL
            let create_table_sql = format!(
                "CREATE TABLE {} (\n{}\n) ;",
                table,
                columns_list.join(",\n")
            );
            create_tables.push(create_table_sql);

            // Add to table names
            table_names.insert(table.clone(), table);
        }
    }

    (create_tables, table_names)
}
```

To integrate this with the existing code, you'll need to:

1. Add the necessary dependencies to your `Cargo.toml`:
```toml
[dependencies]
csv = "1.2"
```

2. Modify the `generate_database_config` function to use the new `add_omdb` function:

```rust
pub fn generate_database_config(config: &Config) {
    let mut table_create_queries: BTreeMap<String, CreateQueries> = BTreeMap::new();
    for v in config.data.values() {
        create_table_1(&mut table_create_queries, v)
    }

    // Add OMDB tables
    let (omdb_tables, omdb_table_names) = add_omdb(config);

    let create_tables: Vec<String> = table_create_queries
        .values()
        .filter(|v| !v.name.contains("-by-"))
        .map(|v| {
            format!(
                "CREATE TABLE {} (
                    item_id int not null,
                    {} {} not null
                );",
                v.name, v.column, v.column_type
            )
        })
        .chain(omdb_tables.into_iter())
        .collect();

    let mut table_names: BTreeMap<String, String> = table_create_queries
        .values()
        .filter(|v| v.level > 1)
        .map(|v| (v.name.clone(), v.name.clone()))
        .collect();

    // Merge OMDB table names
    table_names.extend(omdb_table_names);

    table_names.insert("item".to_string(), "item".to_string());
    table_names.insert("item___label".to_string(), "item___label".to_string());

    // Rest of the function remains the same...
    let kinds: &mut BTreeMap<String, String> = &mut BTreeMap::new();
    for (k, v) in &config.data {
        add_kind(kinds, &k, &v)
    }

    // ... rest of the function
}
```

Key differences from the Python version:
1. Uses Rust's CSV reader instead of pandas
2. Handles file operations with proper error handling
3. Returns both the create table statements and table names
4. Uses Rust's string formatting instead of Python's f-strings
5. All columns are treated as text by default (you may want to adjust the `column_type_sql` function to match your specific needs)

The implementation maintains the same functionality while following Rust's idioms and safety guarantees.