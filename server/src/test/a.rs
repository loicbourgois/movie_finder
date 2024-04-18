use crate::data_2::load_data_2;
use crate::get_movie_images;
use crate::search::search_media;
#[test]
fn test_load_data() {
    // let _ = load_data();
}
#[test]
fn test_search() {
    let data_2 = load_data_2();
    let movie_images = get_movie_images();
    // let results = search("mr robot", &data_2);
    // println!("{results:?}");
    // let results = search("Sean Connery", &data_2);
    // println!("{results:?}");
    // let results = search("science fiction", &data_2);
    // println!("{results:?}");
    // let results = search("titanic", &data_2);
    // println!("{results:?}");
    // let results = search("ghost in the shell", &data_2);
    // println!("{results:?}");

    let results = search_media("ghost in the shell", &data_2, &movie_images);
    println!("{results:?}");
    let _results = search_media("v", &data_2, &movie_images);
    // println!("{results:?}");

    // for x in results.values() {
    //     for y in x {
    //         println!("\nhttps://www.wikidata.org/wiki/{y}");

    //         let ms = get_mappings(y, &data_2);
    //         println!("{ms:?}");
    //     }
    // }
    // assert_eq!(results, vec!["Q18844729"]);
}
