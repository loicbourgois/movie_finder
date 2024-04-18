WITH media AS (
  SELECT * FROM item
  WHERE item.kind IN ('anime', 'documentary')
),

label AS (
  SELECT * FROM item___label
  WHERE language = 'en'
),

media___label AS (
  SELECT * FROM label
),

media___director AS (
  SELECT * FROM item___director
),

director AS (
  SELECT * FROM item
  WHERE item.kind IN ('director')
),

director___label AS (
  SELECT label.*
  FROM label
  INNER JOIN director
    ON label.item_id = director.item_id
),

q AS (
  SELECT
    media.item_id AS media_id,
    media___label.label AS media,
    -- ,media___publication_date.publication_date as release
    media.kind AS media_kind,
    director___label.label AS director,
    director.item_id AS director_id
  FROM media
  INNER JOIN media___label
    ON media.item_id = media___label.item_id
    -- inner join media___publication_date
    --     on media.item_id = media___publication_date.item_id
  INNER JOIN media___director
    ON media.item_id = media___director.item_id
  INNER JOIN director
    ON media___director.director_id = director.item_id
  INNER JOIN director___label
    ON director.item_id = director___label.item_id
)

SELECT *
FROM q
WHERE media_kind = 'anime'
LIMIT 10
