-- file://./../../movie_finder_local/data_v3/database/init_1.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
create type kind AS ENUM (
  'documentary',
'director',
'gender',
'occupation',
'nominated_for',
'award_received',
'genre',
'producer',
'creator',
'screen_writer',
'cast_member',
'narrator',
'characters',
'main_subject',
'original_language',
'composer',
'film_editor',
'inspired_by',
'depicts',
'film',
'film_series',
'western_animation',
'anime',
'animated_television_series',
'television_series',
'country',
'professional_painter',
'professional_artist',
'professional_actor'
);
CREATE TABLE item (
  item_id int not null,
  kind kind not null
);
CREATE TABLE item___label (
  item_id int not null,
  language text not null,
  label text not null
);
CREATE TABLE item___documentary (
            item_id int not null,
            documentary_id int not null
        );
CREATE TABLE item___director (
            item_id int not null,
            director_id int not null
        );
CREATE TABLE item___gender (
            item_id int not null,
            gender_id int not null
        );
CREATE TABLE item___date_of_birth (
            item_id int not null,
            date_of_birth date not null
        );
CREATE TABLE item___occupation (
            item_id int not null,
            occupation_id int not null
        );
CREATE TABLE item___nominated_for (
            item_id int not null,
            nominated_for_id int not null
        );
CREATE TABLE item___award_received (
            item_id int not null,
            award_received_id int not null
        );
CREATE TABLE item___genre (
            item_id int not null,
            genre_id int not null
        );
CREATE TABLE item___producer (
            item_id int not null,
            producer_id int not null
        );
CREATE TABLE item___creator (
            item_id int not null,
            creator_id int not null
        );
CREATE TABLE item___screen_writer (
            item_id int not null,
            screen_writer_id int not null
        );
CREATE TABLE item___publication_date (
            item_id int not null,
            publication_date date not null
        );
CREATE TABLE item___cast_member (
            item_id int not null,
            cast_member_id int not null
        );
CREATE TABLE item___imdb_id (
            item_id int not null,
            imdb_id text not null
        );
CREATE TABLE item___narrator (
            item_id int not null,
            narrator_id int not null
        );
CREATE TABLE item___characters (
            item_id int not null,
            characters_id int not null
        );
CREATE TABLE item___main_subject (
            item_id int not null,
            main_subject_id int not null
        );
CREATE TABLE item___original_language (
            item_id int not null,
            original_language_id int not null
        );
CREATE TABLE item___composer (
            item_id int not null,
            composer_id int not null
        );
CREATE TABLE item___film_editor (
            item_id int not null,
            film_editor_id int not null
        );
CREATE TABLE item___inspired_by (
            item_id int not null,
            inspired_by_id int not null
        );
CREATE TABLE item___depicts (
            item_id int not null,
            depicts_id int not null
        );
CREATE TABLE item___attendance (
            item_id int not null,
            attendance float not null
        );
CREATE TABLE item___duration (
            item_id int not null,
            duration float not null
        );
CREATE TABLE item___omdb_id (
            item_id int not null,
            omdb_id float not null
        );
CREATE TABLE item___box_office (
            item_id int not null,
            box_office float not null
        );
CREATE TABLE item___capital_cost (
            item_id int not null,
            capital_cost float not null
        );
CREATE TABLE item___review_score (
            item_id int not null,
            review_score float not null
        );
CREATE TABLE item___film (
            item_id int not null,
            film_id int not null
        );
CREATE TABLE item___film_series (
            item_id int not null,
            film_series_id int not null
        );
CREATE TABLE item___western_animation (
            item_id int not null,
            western_animation_id int not null
        );
CREATE TABLE item___anime (
            item_id int not null,
            anime_id int not null
        );
CREATE TABLE item___animated_television_series (
            item_id int not null,
            animated_television_series_id int not null
        );
CREATE TABLE item___television_series (
            item_id int not null,
            television_series_id int not null
        );
CREATE TABLE item___country (
            item_id int not null,
            country_id int not null
        );
CREATE TABLE item___professional_painter (
            item_id int not null,
            professional_painter_id int not null
        );
CREATE TABLE item___professional_artist (
            item_id int not null,
            professional_artist_id int not null
        );
CREATE TABLE item___professional_actor (
            item_id int not null,
            professional_actor_id int not null
        );
CREATE TABLE omdb___movie_links (
        source text not null,
    key text not null,
    movie_id int not null,
    language_iso_639_1 text not null
) ;
CREATE TABLE omdb___image_ids (
        image_id int not null,
    object_id int ,
    object_type text ,
    image_version int 
) ;
CREATE TABLE omdb___movie_references (
        movie_id int not null,
    referenced_id int not null,
    type text 
) ;
CREATE TABLE omdb___category_names (
        category_id int not null,
    name text not null,
    language_iso_639_1 text not null
) ;
CREATE TABLE omdb___movie_categories (
        movie_id int not null,
    category_id int not null
) ;
CREATE TABLE omdb___all_categories (
        id int not null,
    parent_id int ,
    root_id int not null
) ;
CREATE TABLE omdb___all_votes (
        movie_id int not null,
    vote_average float not null,
    votes_count int not null
) ;
CREATE TABLE omdb___all_movies (
        id int not null,
    name text not null,
    parent_id int ,
    date date 
) ;
CREATE TABLE omdb___all_series (
        id int not null,
    name text not null,
    parent_id int ,
    date date 
) ;
