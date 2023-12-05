with media as (
    select 
        item___label.label, 
        item___label.language, 
        item.*
    from item
    inner join item___label
        on item.item_id = item___label.item_id
)
,media___director as (
    select 
        item___label.label, 
        item___label.language, 
        item___director.*
    from item___director
    inner join item___label
        on item___director.director_id = item___label.item_id
)
,director___gender as (
    select 
        item___label.label, 
        item___label.language, 
        item___gender.*
    from item___gender
    inner join item___label
        on item___gender.gender_id = item___label.item_id
)
,media___creator as (
    select 
        item___label.label, 
        item___label.language, 
        item___creator.*
    from item___creator
    inner join item___label
        on item___creator.creator_id = item___label.item_id
)
,media___publication_date as (
    select * 
    from item___publication_date
)
, q as (
    select
        media.item_id as media_id
        ,media.label as media
        ,media.kind as kind
        ,media___director.label as director
        ,media___creator.label as creator
        ,media___publication_date.publication_date as publication_date
        -- ,media___director.item_id as director_id
        -- ,director___gender.label as director_gender
    from media
    left outer join media___director
        on media.item_id = media___director.item_id
    left outer join director___gender
        on media___director.director_id = director___gender.item_id
    left outer join media___creator
        on media.item_id = media___creator.item_id
    left outer join media___publication_date
        on media.item_id = media___publication_date.item_id
    where
        media.language = 'en'
        and (media___director.language = 'en' or media___director.language is null)
        and (media___creator.language = 'en' or media___creator.language is null)
        and (director___gender.language = 'en' or director___gender.language is null)
)
select distinct *
from q
where 
    media ilike '%christ%'
    -- director ilike 'Christopher Nolan'
    -- or  creator ilike 'trey parker'
limit 100
