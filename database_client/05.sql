WITH media AS (
  SELECT
    item.*,
    item___label.label,
    item___label.language
  FROM item
  INNER JOIN item___label
    ON item.item_id = item___label.item_id
),

media___director AS (
  SELECT
    item___director.*,
    item___label.label,
    item___label.language
  FROM item___director
  INNER JOIN item___label
    ON item___director.director_id = item___label.item_id
),

director___gender AS (
  SELECT
    item___gender.*,
    item___label.label,
    item___label.language
  FROM item___gender
  INNER JOIN item___label
    ON item___gender.gender_id = item___label.item_id
),

media___creator AS (
  SELECT
    item___creator.*,
    item___label.label,
    item___label.language
  FROM item___creator
  INNER JOIN item___label
    ON item___creator.creator_id = item___label.item_id
),

media___publication_date AS (
  SELECT *
  FROM item___publication_date
),

q AS (
  SELECT
    media.item_id AS media_id,
    media.label AS media,
    media.kind AS kind,
    media___director.label AS director,
    media___creator.label AS creator,
    media___publication_date.publication_date AS publication_date
  -- ,media___director.item_id as director_id
  -- ,director___gender.label as director_gender
  FROM media
  LEFT OUTER JOIN media___director
    ON media.item_id = media___director.item_id
  LEFT OUTER JOIN director___gender
    ON media___director.director_id = director___gender.item_id
  LEFT OUTER JOIN media___creator
    ON media.item_id = media___creator.item_id
  LEFT OUTER JOIN media___publication_date
    ON media.item_id = media___publication_date.item_id
  WHERE
    media.language = 'en'
    AND (media___director.language = 'en' OR media___director.language IS null)
    AND (media___creator.language = 'en' OR media___creator.language IS null)
    AND (
      director___gender.language = 'en' OR director___gender.language IS null
    )
)

SELECT DISTINCT *
FROM q
WHERE
  media ILIKE '%christ%'
-- director ilike 'Christopher Nolan'
-- or  creator ilike 'trey parker'
LIMIT 100
