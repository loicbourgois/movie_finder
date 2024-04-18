WITH person AS (
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

director___media AS (
  SELECT
    item___director.*,
    item___label.label,
    item___label.language
  FROM item___director
  INNER JOIN item___label
    ON item___director.item_id = item___label.item_id
),

creator___media AS (
  SELECT
    item___creator.*,
    item___label.label,
    item___label.language
  FROM item___creator
  INNER JOIN item___label
    ON item___creator.item_id = item___label.item_id
),

q AS (
  SELECT
    person.item_id AS person_id,
    person.label AS person,
    director___media.label AS directed,
    creator___media.label AS created
  FROM person
  LEFT OUTER JOIN director___media
    ON person.item_id = director___media.director_id
  LEFT OUTER JOIN creator___media
    ON person.item_id = creator___media.creator_id
  WHERE
    person.language = 'en'
-- and (media___director.language = 'en' or media___director.language is null)
-- and (media___creator.language = 'en' or media___creator.language is null)
-- and (director___gender.language = 'en' or director___gender.language is null)
)

SELECT DISTINCT *
FROM q
WHERE
  -- person ilike '%christ%nolan%'
  -- director ilike 'Christopher Nolan'
  person ILIKE 'trey parker'
LIMIT 100
