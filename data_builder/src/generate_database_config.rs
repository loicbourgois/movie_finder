use crate::config::Config;
use std::collections::BTreeMap;
use std::collections::BTreeSet;
use std::fs;
use csv::ReaderBuilder;
use std::path::PathBuf;

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

pub fn generate_database_config(config: &Config) {
    let mut table_create_queries: BTreeMap<String, CreateQueries> = BTreeMap::new();
    for v in config.data.values() {
        create_table_1(&mut table_create_queries, v)
    }
    let mut create_tables: Vec<String> = table_create_queries
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
        .collect();
    let mut table_names: BTreeMap<String, String> = table_create_queries
        .values()
        .filter(|v| v.level > 1)
        .map(|v| (v.name.clone(), v.name.clone()))
        .collect();
    table_names.insert("item".to_string(), "item".to_string());
    table_names.insert("item___label".to_string(), "item___label".to_string());
    
    
    add_omdb(config, &mut create_tables, &mut table_names);
    
    
    let kinds: &mut BTreeMap<String, String> = &mut BTreeMap::new();
    for (k, v) in &config.data {
        add_kind(kinds, &k, &v)
    }
    let kinds_str = kinds
        .keys()
        .map(|k| format!("'{}'", k))
        .collect::<Vec<_>>()
        .join(",\n");

    let import_csv = table_names.keys()
        .map(|table_name| {
            format!(
                "    -c \"\\copy {} FROM '$HOME/github.com/loicbourgois/movie_finder_local/data_v3/database/{}.csv' CSV HEADER;\" \\",
                table_name, table_name
            )
        })
        .collect::<Vec<_>>()
        .join("\n");
    let home_dir = std::env::var("HOME").expect("HOME environment variable not set");
    let path = PathBuf::from(home_dir.clone())
        .join("github.com/loicbourgois/movie_finder/database/go_inner.template.sh");
    let go_inner_template = read(&path);
    let go_inner_rendered = go_inner_template.replace("{IMPORT_CSV}", &import_csv);
    let path = PathBuf::from(home_dir.clone())
        .join("github.com/loicbourgois/movie_finder/database/go_inner_rs.sh");
    write_force(&path, &go_inner_rendered);
    let create_table_str = create_tables.join("\n");
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



fn get_nullability_omdb(ck: &str) -> String {
    (match ck {
            "image_id"=> "not null",
            "object_id"=> "",
            "object_type"=> "",
            "image_version"=> "",
            "type"=> "",
            "parent_id"=> "",
            "date"=> "",
        _ => "not null",
    })
    .to_string()
}

fn get_column_type_sql_omdb(ck: &str) -> String {
    (match ck {
            "image_id"=> "int",
            "object_id"=> "int",
            "object_type"=> "text",
            "image_version"=> "int",
            "source"=> "text",
            "key"=> "text",
            "language_iso_639_1"=> "text",
            "name"=> "text",
            "type"=> "text",
            "vote_average"=> "float",
            "date"=> "date",
        _ => "int",
    })
    .to_string()
}


fn add_omdb(
    config: &Config,
    create_tables: &mut Vec<String>,
    table_names: &mut BTreeMap<String, String>,
)  {
    for omdb_name in &config.omdb {
        let short_path = format!("omdb/{}", omdb_name);
        let table_name = format!("omdb___{}", omdb_name);
        let home_dir = std::env::var("HOME").expect("HOME environment variable not set");
        let csv_path = PathBuf::from(home_dir.clone())
            .join("github.com/loicbourgois/movie_finder_local/data_v3/csv")
            .join(format!("{short_path}.csv"));
        let mut reader = ReaderBuilder::new()
            .has_headers(true)
            .flexible(true)
            .from_path(&csv_path).unwrap();
        let headers = reader.headers().unwrap().clone();
        let mut columns_sql = Vec::new();
        for column_name in headers.iter() {
            let column_type = get_column_type_sql_omdb(column_name);
            let nullability = get_nullability_omdb(column_name);
            columns_sql.push(format!("    {} {} {}", column_name, column_type, nullability));
        }
        let sep = ",\n";
        let columns_sql_str = columns_sql.join(&format!("{sep}"));
        let create_stmt = format!(
            "CREATE TABLE {} (\n{}\n);",
            table_name, columns_sql_str
        );
        create_tables.push(create_stmt);
        table_names.insert(table_name.clone(), table_name);
    }
}
