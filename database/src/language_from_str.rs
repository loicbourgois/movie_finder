use crate::Language;

pub fn language_from_str(s: &str) -> Language {
    match s {
        "fr" => Language::French,
        "en" => Language::English,
        "ja" => Language::Japanese,
        // "sa" => Language::Spanish,
        "es" => Language::Spanish,
        "yue" => Language::Cantonese,
        "zh" => Language::Chinese,
        "cmn" => Language::MandarinChinese,
        "hi" => Language::Hindi,

        _ => panic!("error in language_from_str: {s}"),
    }
}
