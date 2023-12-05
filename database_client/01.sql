with media as (
    select * from item
    where item.kind in ('anime', 'documentary')
)
, label as (
    select * from item___label
    where language = 'en'
)
,media___label as (
    select * from label
)
,media___director as (
    select * from item___director
)
,director as (
    select * from item
    where item.kind in ('director')
)
,director___label as (
    select label.* 
    from label
    inner join director
    on director.item_id = label.item_id
)
, q as (
    select
        media.item_id as media_id
        ,media___label.label as media
        -- ,media___publication_date.publication_date as release
        ,media.kind as media_kind
        ,director___label.label as director
        ,director.item_id as director_id
    from media
    inner join media___label
        on media.item_id = media___label.item_id
    -- inner join media___publication_date
    --     on media.item_id = media___publication_date.item_id
    inner join media___director
        on media.item_id = media___director.item_id
    inner join director
        on media___director.director_id = director.item_id
    inner join director___label
        on director.item_id = director___label.item_id
)
select *
from q
where media_kind = 'anime'
limit 10
