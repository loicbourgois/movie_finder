-- \d


with q1 as (
    select * from omdb___image_ids
    where object_id = 1
)
, q2 as (
    select * 
    from omdb___movie_links
    where source = 'imdbmovie'
)
, q3 as (
    select * 
    from item___omdb_id
)
, q4 as (
    select
        item_id,
        movie_id as omdb_id
    from item___imdb_id
    inner join omdb___movie_links
    on item___imdb_id.imdb_id = omdb___movie_links.key
    where source = 'imdbmovie'
    union all 
    select * from item___omdb_id
)
, item___omdb_id___v2 as (
    select * from q4
    group by item_id, omdb_id
)
, q5 as (
    select
        a.item_id,
        image_id as omdb_image_id,
        image_version as omdb_image_version
    from item___omdb_id___v2  as a
    inner join omdb___image_ids as b
    on a.omdb_id = b.object_id
    inner join item as c
    on a.item_id = c.item_id
    where 
        (kind = 'film' and object_type = 'Movie')
        or (kind = 'television_series' and object_type = 'Movie')
)
, q6 as (
    select
        item_id,
        omdb_image_id,
        count(*) as c,
        array_agg(omdb_image_version) as omdb_image_versions,
        max(omdb_image_version) as omdb_image_version_max
    from q5
    group by item_id, omdb_image_id
)
, item___omdb_image as (
    select
        item_id,
        coalesce(
            'https://www.omdb.org/image/default/' || omdb_image_id || '.jpeg?v=' || omdb_image_version_max,
            'https://www.omdb.org/image/default/' || omdb_image_id || '.jpeg' 
        ) as url
        
    from q6
)
--select count(*) from item___omdb_image;

select * from item___omdb_image
where item_id = 478360
limit 10;

select distinct kind from item;
-- \d+ omdb___image_ids
