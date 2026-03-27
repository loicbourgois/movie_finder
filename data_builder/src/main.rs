mod config;
mod generate_database_config;
mod convert_to_sql;
use crate::config::get_config;
use crate::generate_database_config::generate_database_config;
use crate::convert_to_sql::convert_to_sql;

fn main() {
    println!("start");
    let config = get_config();
    convert_to_sql(&config);
    generate_database_config(&config);
}
