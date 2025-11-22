use crate::Kind;

pub fn kind_from_str(s: &str) -> Kind{
    match s {
        "anime" => Kind::Anime,
        "documentary" => Kind::Documentary,
        _ => panic!("error in str_to_kind: {s}"),
    }
}