WITH media AS (
  SELECT
    item___label.label AS media,
    item___label.language AS media_language,
    item.item_id AS media_id,
    item.kind AS media_kind
  FROM item
  INNER JOIN item___label
    ON item.item_id = item___label.item_id
  WHERE
    item.kind IN ('documentary') AND item___label.label ILIKE '%beau%'
), media_director AS (
  SELECT
    item___label.label AS media_director,
    item___label.language AS media_director_language,
    item___director.item_id AS media_director_up_id,
    item___director.director_id AS media_director_id
  FROM item___director
  INNER JOIN item___label
    ON item___director.director_id = item___label.item_id
  WHERE
    TRUE
), media_director_gender AS (
  SELECT
    item___label.label AS media_director_gender,
    item___label.language AS media_director_gender_language,
    item___gender.item_id AS media_director_gender_up_id,
    item___gender.gender_id AS media_director_gender_id
  FROM item___gender
  INNER JOIN item___label
    ON item___gender.gender_id = item___label.item_id
  WHERE
    TRUE
), q_all AS (
  SELECT DISTINCT
    *
  FROM media
  LEFT OUTER JOIN media_director
    ON media.media_id = media_director.media_director_up_id
  LEFT OUTER JOIN media_director_gender
    ON media_director.media_director_id = media_director_gender.media_director_gender_up_id
), q_limit AS (
  SELECT DISTINCT
    media_id
  FROM q_all
  LIMIT 2
)
SELECT
  q_all.*
FROM q_all
INNER JOIN q_limit
  ON q_all.media_id = q_limit.media_id