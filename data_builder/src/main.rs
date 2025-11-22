mod config;
mod generate_database_config;
use crate::config::get_config;
use crate::generate_database_config::generate_database_config;

fn main() {
    println!("start");
    let config = get_config();
    generate_database_config(&config);
}
