with media as (
    select * from item
    where item.kind in ('anime', 'documentary', 'film')
)
,media___label as (
    select * from item___label
)
,media___director as (
    select * from item___director
)
,director as (
    select * from item
    where item.kind in ('director')
)
,director___label as (
    select * 
    from item___label
)
, q as (
    select
        media.item_id as media_id
        ,media___label.label as media
        -- ,media___publication_date.publication_date as release
        ,media.kind as media_kind
        ,director___label.label as director
        ,director.item_id as director_id
    from media, media___label, director___label, director, media___director
    where
        media.item_id = media___label.item_id
        and  media.item_id = media___director.item_id
        and media___director.director_id = director.item_id
        and director.item_id = director___label.item_id
        and media___label.language = 'en'
        and director___label.language = 'en'
)
select *
from q
-- where media_kind = 'anime'
where director ilike '%tom tykwer%'
limit 100
