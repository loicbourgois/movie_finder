with
qlabel as (
    select * from item___label
    where language = 'fr'
)

, qs1 as (
    select item_id as id, 1 as rank, label
    from qlabel
    where label ilike '%psycho%thriller%'
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

, q3 as (
    select * from qs1
    union all
    select * from qs2
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
)

, q6 as (
    select
        id as i1,
        label as l1,
        rank as r1,
        kind as k1
    from q5
)

, q7 as (
    select
        q6.i1
        , array_agg(distinct q6.l1) as l1
        , min(q6.r1) as r1
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
