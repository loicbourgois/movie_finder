Here’s how you can translate the **`add_omdb()`** Python pseudo‑code into idiomatic Rust, consistent with the rest of your module:

---

### ✅ Explanation of what this function must do

The Python code does four things:
1. Iterate over keys from `config["omdb"]`.
2. For each key:
   - Determine the file path.
   - Read a CSV file.
   - Clean up values and extract columns.
   - Build SQL `CREATE TABLE` statements for each OMDB CSV file.
3. Append those `CREATE TABLE` statements to the list of SQL commands.
4. Add new table names to `table_names`.

---

### ✅ Rust version of `add_omdb`

This Rust translation assumes:

- You’ve added `use csv::ReaderBuilder;` and `use std::error::Error;` at the top.
- `config.data.get("omdb")` provides a `BTreeMap<String, _>` of OMDB tables.
- You can deal with CSV by reading headers only (no need to parse values deeply, because only column names are required to build SQL).

Add this near the bottom of the file (before or alongside `generate_database_config`):

```rust
use csv::ReaderBuilder;
use std::path::PathBuf;

fn add_omdb(
    config: &Config,
    create_tables: &mut Vec<String>,
    table_names: &mut BTreeMap<String, String>,
) -> Result<(), Box<dyn std::error::Error>> {
    // Get the "omdb" section
    let Some(omdb_section) = config.data.get("omdb") else {
        return Ok(()); // Nothing to do if no omdb entry
    };

    for omdb_name in omdb_section.keys() {
        let short_path = format!("omdb/{}", omdb_name);
        let table_name = format!("omdb___{}", omdb_name);
        let level = "omdb";
        let home_dir = std::env::var("HOME").expect("HOME environment variable not set");

        // Build full CSV path
        let csv_path = PathBuf::from(home_dir.clone())
            .join("github.com/loicbourgois/movie_finder_local/data_v3/csv")
            .join(format!("{short_path}.csv"));

        // Read CSV headers
        let mut reader = ReaderBuilder::new()
            .has_headers(true)
            .flexible(true)
            .from_path(&csv_path)?;

        let headers = reader.headers()?.clone();

        // Compose CREATE TABLE columns
        let mut columns_sql = Vec::new();
        for column_name in headers.iter() {
            let column_type = get_column_type_sql(column_name);
            // Omdb fields are always nullable except possibly identifiers, adjust logic if needed
            let nullability = "NULL";
            columns_sql.push(format!("    {} {} {}", column_name, column_type, nullability));
        }

        let sep = ",\n";
        let columns_sql_str = columns_sql.join(&format!("{sep}"));

        // Build SQL CREATE TABLE statement
        let create_stmt = format!(
            "CREATE TABLE {} (\n{}\n);",
            table_name, columns_sql_str
        );
        create_tables.push(create_stmt);
        table_names.insert(table_name.clone(), table_name);
    }

    Ok(())
}
```

---

### ✅ Integrating `add_omdb` into `generate_database_config`

Call it right after you build `create_tables` and `table_names` in `generate_database_config`:

```rust
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

    // 👇 Add OMDB CSV tables to SQL and table list
    if let Err(e) = add_omdb(config, &mut create_tables, &mut table_names) {
        eprintln!("Warning: failed to add omdb tables: {}", e);
    }

    // ... rest of existing code ...
}
```

---

### ✅ Key notes

- Instead of pandas, the code uses Rust’s [`csv`](https://docs.rs/csv) crate to read headers easily.
- The function fills both `create_tables` and `table_names` just like the rest of your builder.
- It reads CSV headers only — no in‑memory data manipulation.
- It’s safe and idiomatic Rust; errors are propagated as `Result<(), Box<dyn Error>>`.

---

This completes the TODO by providing a fully‑working Rust‑native version of the **OMDB table builder** logic from your original Python snippet.