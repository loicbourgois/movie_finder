```rust
use crate::config::Config;
use std::collections::BTreeMap;
use std::collections::BTreeSet;
use std::fs;
use std::path::PathBuf;
use csv; // Add this dependency to Cargo.toml under [dependencies]: csv = "1.1"

fn get_column_name(ck: &str) -> String {
    (match ck {
        "date_of_birth" => "date_of_birth",
        "publication_date" => "publication_date",
        "attendance" => "attendance",
        "duration" => "duration",
        "box_office" => "box_office",
        "capital_cost" => "capital_cost",
        "omdb_id" => "omdb_id",
        "review_score" => "review_score",
        "imdb_id" => "imdb_id",
        _ => return format!("{ck}_id"),
    })
    .to_string()
}

fn get_column_type(ck: &str) -> String {
    (match ck {
        "date_of_birth" => "date",
        "publication_date" => "date",
        "attendance" => "numeric",
        "duration" => "numeric",
        "box_office" => "numeric",
        "capital_cost" => "numeric",
        "omdb_id" => "numeric",
        "review_score" => "review_score",
        "imdb_id" => "string",
        _ => "qid",
    })
    .to_string()
}

fn get_column_type_sql(ck: &str) -> String {
    (match ck {
        "date_of_birth" => "date",
        "publication_date" => "date",
        "attendance" => "float",
        "duration" => "float",
        "box_office" => "float",
        "capital_cost" => "float",
        "omdb_id" => "float",
        "review_score" => "float",
        "imdb_id" => "text",
        _ => "int",
    })
    .to_string()
}

struct CreateQueries {
    name: String,
    column: String,
    column_type: String,
    level: usize,
}

fn create_table_3(table_create_queries: &mut BTreeMap<String, CreateQueries>, k3: &str) {
    let column_type = get_column_type(&get_column_name(k3));
    let column = if column_type == "qid" {
        format!("{k3}_id")
    } else {
        k3.to_string()
    };
    table_create_queries.insert(
        k3.to_string(),
        CreateQueries {
            name: format!("item___{k3}"),
            column: column,
            column_type: get_column_type_sql(&get_column_name(k3)),
            level: 3,
        },
    );
}

fn create_table_2(
    table_create_queries: &mut BTreeMap<String, CreateQueries>,
    k2: &str,
    v2: &BTreeSet<String>,
) {
    let column_type = get_column_type(&get_column_name(k2));
    let column = if column_type == "qid" {
        format!("{k2}_id")
    } else {
        k2.to_string()
    };
    table_create_queries.insert(
        k2.to_string(),
        CreateQueries {
            name: format!("item___{k2}"),
            column: column,
            column_type: get_column_type_sql(&get_column_name(k2)),
            level: 2,
        },
    );
    for k3 in v2 {
        create_table_3(table_create_queries, k3)
    }
}

fn create_table_1(
    table_create_queries: &mut BTreeMap<String, CreateQueries>,
    v: &BTreeMap<String, BTreeSet<String>>,
) {
    for (k2, v2) in v {
        create_table_2(table_create_queries, k2, v2)
    }
}

fn add_kind(kinds: &mut BTreeMap<String, String>, k: &str, v: &BTreeMap<String, BTreeSet<String>>) {
    if get_column_type(&get_column_name(k)) == "qid" {
        kinds.insert(k.to_string(), k.to_string());
    }
    for (k2, v2) in v {
        if get_column_type(&get_column_name(k2)) == "qid" {
            kinds.insert(k2.to_string(), k2.to_string());
        }
        for k3 in v2 {
            if get_column_type(&get_column_name(k3)) == "qid" {
                kinds.insert(k3.to_string(), k3.to_string());
            }
        }
    }
}

fn read(path: &PathBuf) -> String {
    fs::read_to_string(path).unwrap()
}

fn write_force(path: &PathBuf, contents: &str) -> () {
    fs::write(path, contents).unwrap()
}

// Helper function to determine SQL column type for OMDB tables
fn get_omdb_column_type_sql(column_name: &str) -> String {
    match column_name {
        // Common OMDB fields and their likely SQL types
        "imdbID" => "text",
        "Year" => "int",
        "Released" => "date",
        "DVD" => "date",
        "Metascore" => "float",
        "imdbRating" => "float",
        "imdbVotes" => "int", // Will need cleaning during import if it contains commas
        "BoxOffice" => "float", // Will need cleaning during import if it contains '$' or commas
        "Response" => "text", // "True" or "False"
        _ => "text", // Default to text for most string-based fields
    }
    .to_string()
}

// Helper function to determine SQL column nullability for OMDB tables
fn get_omdb_column_nullability_sql(column_name: &str) -> String {
    match column_name {
        "imdbID" => "NOT NULL", // imdbID is a primary identifier, usually not nullable
        _ => "",                // Most other columns are generally nullable
    }
    .to_string()
}

// Rust equivalent of the Python `add_omdb` function
fn add_omdb_tables(
    config: &Config,
    omdb_create_tables: &mut Vec<String>,
    all_table_names: &mut BTreeMap<String, String>,
    home_dir: &str,
) {
    // Assuming config.omdb is a BTreeMap<String, String> or BTreeMap<String, ()>
    // where the keys are the names of the OMDB datasets (e.g., "movies", "series").
    for name in config.omdb.keys() {
        let short_path = format!("omdb/{name}");
        let table_name = format!("omdb___{name}");

        let csv_path_str = format!(
            "{}/github.com/loicbourgois/movie_finder_local/data_v3/csv/{short_path}.csv",
            home_dir
        );
        let csv_path = PathBuf::from(&csv_path_str);

        // Read CSV header to get column names dynamically
        let mut reader = match csv::ReaderBuilder::new()
            .has_headers(true)
            .from_path(&csv_path)
        {
            Ok(r) => r,
            Err(e) => {
                eprintln!(
                    "Warning: Could not read CSV file for OMDB table '{}' at '{}': {}",
                    table_name,
                    csv_path.display(),
                    e
                );
                continue; // Skip this OMDB item if file cannot be read
            }
        };

        let headers = match reader.headers() {
            Ok(h) => h,
            Err(e) => {
                eprintln!(
                    "Warning: Could not read headers from OMDB CSV '{}': {}",
                    csv_path.display(),
                    e
                );
                continue;
            }
        };

        let mut columns_list = Vec::new();
        for column_name_record in headers.iter() {
            let column_name = column_name_record.to_string();
            let column_type = get_omdb_column_type_sql(&column_name);
            let nullability = get_omdb_column_nullability_sql(&column_name);

            // Format column definition, omitting "NOT NULL" if it's an empty string
            let column_def = if nullability.is_empty() {
                format!("    {} {}", column_name, column_type)
            } else {
                format!("    {} {} {}", column_name, column_type, nullability)
            };
            columns_list.push(column_def);
        }

        let sep = ",\n";
        omdb_create_tables.push(format!(
            "CREATE TABLE {} (\n{}\n) ;",
            table_name,
            columns_list.join(sep)
        ));
        all_table_names.insert(table_name.clone(), table_name);
    }
}

pub fn generate_database_config(config: &Config) {
    let mut data_derived_table_create_queries: BTreeMap<String, CreateQueries> = BTreeMap::new();
    for v in config.data.values() {
        create_table_1(&mut data_derived_table_create_queries, v)
    }

    let mut data_derived_create_tables: Vec<String> = data_derived_table_create_queries
        .values()
        .filter(|v| !v.name.contains("-by-")) // Filter out 'by' tables
        .map(|v| {
            format!(
                "CREATE TABLE {} (
                    item_id int not null,
                    {} {} not null
                );",
                v.name, v.column, v.column_type
            )
        })
        .collect();

    let mut all_table_names: BTreeMap<String, String> = data_derived_table_create_queries
        .values()
        .filter(|v| v.level > 1) // Only add level > 1 tables from 'data' for import list
        .map(|v| (v.name.clone(), v.name.clone()))
        .collect();
    all_table_names.insert("item".to_string(), "item".to_string());
    all_table_names.insert("item___label".to_string(), "item___label".to_string());

    let kinds: &mut BTreeMap<String, String> = &mut BTreeMap::new();
    for (k, v) in &config.data {
        add_kind(kinds, k, v)
    }

    let home_dir = std::env::var("HOME").expect("HOME environment variable not set");

    // Collection for OMDB-specific CREATE TABLE statements
    let mut omdb_create_tables: Vec<String> = Vec::new();
    // Call the new Rust function to add OMDB tables and their names
    add_omdb_tables(config, &mut omdb_create_tables, &mut all_table_names, &home_dir);

    // Combine all CREATE TABLE statements from both data sources
    let mut all_create_tables: Vec<String> = data_derived_create_tables;
    all_create_tables.extend(omdb_create_tables);

    let kinds_str = kinds
        .keys()
        .map(|k| format!("'{}'", k))
        .collect::<Vec<_>>()
        .join(",\n");

    let import_csv = all_table_names.keys() // Use combined table names for import list
        .map(|table_name| {
            format!(
                "    -c \"\\copy {} FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/{}.csv' CSV HEADER;\" \\",
                table_name, table_name
            )
        })
        .collect::<Vec<_>>()
        .join("\n");
    
    let path = PathBuf::from(home_dir.clone())
        .join("github.com/loicbourgois/movie_finder/database/go_inner.template.sh");
    let go_inner_template = read(&path);
    let go_inner_rendered = go_inner_template.replace("{IMPORT_CSV}", &import_csv);
    let path = PathBuf::from(home_dir.clone())
        .join("github.com/loicbourgois/movie_finder/database/go_inner_rs.sh");
    write_force(&path, &go_inner_rendered);

    // Use the combined list of all CREATE TABLE statements
    let create_table_str = all_create_tables.join("\n");
    let path = PathBuf::from(home_dir.clone())
        .join("github.com/loicbourgois/movie_finder/database/init_1.template.sql");
    let init_1_template = read(&path);
    let init_1_rendered = init_1_template
        .replace("{create_table_str}", &create_table_str)
        .replace("{kinds_str}", &kinds_str);
    let path = PathBuf::from(home_dir.clone())
        .join("github.com/loicbourgois/movie_finder/database/init_1_rs.sql");
    write_force(&path, &init_1_rendered);
}
```