WITH media AS (
    SELECT *
    FROM item
    WHERE item.kind IN ('anime', 'documentary', 'film')
),

media___label AS (
    SELECT * FROM item___label
),

media___director AS (
    SELECT * FROM item___director
),

director AS (
    SELECT * FROM item
    WHERE item.kind IN ('director')
),

director___label AS (
    SELECT *
    FROM item___label
),

q AS (
    SELECT
        media.item_id AS media_id,
        media___label.label AS media,
        media.kind AS media_kind,
        director___label.label AS director,
        director.item_id AS director_id
    FROM media, media___label, director___label, director, media___director
    WHERE
        media.item_id = media___label.item_id
        AND media.item_id = media___director.item_id
        AND media___director.director_id = director.item_id
        AND director.item_id = director___label.item_id
)

SELECT *
FROM q
WHERE director ILIKE '%tom tykwer%'
LIMIT 100
