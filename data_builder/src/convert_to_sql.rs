use crate::config::Config;

struct Todo {
    // short_path: String,
    // "short_path": "documentary",
    // "table": "item",
    // "type": "documentary",
    // "level": 1

    // "short_path": "fr/documentary/characters",
    // "k": "characters",
    // "level": "label"
}

fn get_todos(_config: &Config) -> Vec<Todo> {
    Vec::new()
}




pub fn convert_to_sql(config: &Config) {
    let _todos = get_todos(config);
    // write_force(
    //     "/root/github.com/loicbourgois/movie_finder/data_builder/convert_to_sql.todos.py.json",
    //     json.dumps(todos, indent=2)
    // )
}