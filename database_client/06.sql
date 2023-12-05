with person as (
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
,director___media as (
    select 
        item___label.label, 
        item___label.language, 
        item___director.*
    from item___director
    inner join item___label
        on item___director.item_id = item___label.item_id
)
,creator___media as (
    select 
        item___label.label, 
        item___label.language, 
        item___creator.*
    from item___creator
    inner join item___label
        on item___creator.item_id = item___label.item_id
)
, q as (
    select
        person.item_id as person_id
        ,person.label as person
        ,director___media.label as directed
        ,creator___media.label as created
    from person
    left outer join director___media
        on person.item_id = director___media.director_id
    left outer join creator___media
        on person.item_id = creator___media.creator_id
    where
        person.language = 'en'
        -- and (media___director.language = 'en' or media___director.language is null)
        -- and (media___creator.language = 'en' or media___creator.language is null)
        -- and (director___gender.language = 'en' or director___gender.language is null)
)
select distinct *
from q
where 
    -- person ilike '%christ%nolan%'
    -- director ilike 'Christopher Nolan'
    person ilike 'trey parker'
limit 100
