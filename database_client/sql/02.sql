-- SELECT * FROM item___label
-- where label ilike '%Robert De Niro%'
-- limit 10;
-- -- select * 
-- -- from item___anime
-- -- from item___cast_member
-- -- limit 10
-- select * from item
-- where item_id = 36949;

-- select * from item___cast_member
-- where cast_member_id = 45772;

-- select count(*) from item;
-- with q1 as (
--     select distinct item_id from item
-- )
-- select count(*) from q1;


with
qlabel as (
    select * from item___label
    where language = 'fr'
)

, qs1 as (
    select item_id as id, 1 as rank, label
    from qlabel
    where label ilike '%psycho%thriller%'
    -- where label ilike '%titanic%'
    group by item_id, label
)

, qs2 as (
    select item_id as id, 2 as rank, label
    from qlabel
    where
        label ilike '%psycho%'
        and label ilike '%thriller%'
    group by item_id, label
)
-- , qs3 as (
--     select item_id as id, 3 as rank, label
--     from qlabel
--     where label ilike '%thriller%'
--         or label ilike '%psycho%'
--     group by item_id, label
-- )

, q3 as (
    select * from qs1
    union all
    select * from qs2
    -- union all
    -- select * from qs3
)

, q4 as (
    select * from q3
    inner join item
        on q3.id = item.item_id
)

, q5 as (
    select
        id
        -- ,min(rank) as rank
        -- ,array_agg(distinct kind) as kind
        -- ,array_agg(distinct label) as label
        , rank
        , kind
        , label
    from q4
    -- group by id
    -- order by rank
)

, q6 as (
    select
        id as i1,
        label as l1,
        rank as r1,
        kind as k1
    from q5
    -- where rank <= 2
)

, q7 as (
    select
        q6.i1
        , array_agg(distinct q6.l1) as l1
        , min(q6.r1) as r1
        -- ,q6.k1
        , a.item_id as i2
        , array_agg(distinct b.label) as l2
        , array_agg(distinct c.kind) as k2
    from q6
    inner join item___genre as a
        on a.genre_id = q6.i1
    inner join qlabel as b
        on a.item_id = b.item_id
    inner join item as c
        on b.item_id = c.item_id
    group by i1, i2
)

select * from q7

;


-- select * from item___genre limit 10;

-- \d
