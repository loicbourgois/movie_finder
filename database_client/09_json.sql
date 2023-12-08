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
    item.kind IN ('documentary')
), director_gender AS (
  SELECT
    item___label.label AS gender,
    item___label.language AS gender_language,
    item___gender.item_id AS gender_up_id,
    item___gender.gender_id AS gender_id
  FROM item___gender
  INNER JOIN item___label
    ON item___gender.gender_id = item___label.item_id
  WHERE
    TRUE
), media_director AS (
  SELECT
    item___label.label AS director,
    item___label.language AS director_language,
    item___director.item_id AS director_up_id,
    item___director.director_id AS director_id
  FROM item___director
  INNER JOIN item___label
    ON item___director.director_id = item___label.item_id
  WHERE
    TRUE
), director_gender_j AS (
  SELECT
    gender_up_id,
    gender_id,
    JSON_BUILD_OBJECT('label', JSON_OBJECT_AGG(gender_language, gender)) AS gender_data
  FROM director_gender
  GROUP BY
    gender_up_id,
    gender_id
), media_director_j AS (
  SELECT
    director_up_id,
    director_id,
    JSON_BUILD_OBJECT(
      'label',
      JSON_OBJECT_AGG(director_language, director),
      'gender',
      COALESCE(
        JSON_OBJECT_AGG(gender_id, gender_data) FILTER(WHERE
          NOT gender_id IS NULL),
        CAST('{}' AS JSON)
      )
    ) AS director_data
  FROM media_director
  LEFT OUTER JOIN director_gender_j
    ON media_director.director_id = director_gender_j.gender_up_id
  GROUP BY
    director_up_id,
    director_id
), media_j AS (
  SELECT
    media_id,
    JSON_BUILD_OBJECT(
      'label',
      JSON_OBJECT_AGG(media_language, media),
      'kind',
      media.media_kind,
      'director',
      COALESCE(
        JSON_OBJECT_AGG(director_id, director_data) FILTER(WHERE
          NOT director_id IS NULL),
        CAST('{}' AS JSON)
      )
    ) AS media_data
  FROM media
  LEFT OUTER JOIN media_director_j
    ON media.media_id = media_director_j.director_up_id
  GROUP BY
    media.media_id,
    media.media_kind
), q_limit AS (
  SELECT DISTINCT
    media_id
  FROM media_j
  LIMIT 2
), q2 AS (
  SELECT
    JSON_OBJECT_AGG(media_j.media_id, media_j.media_data) AS data
  FROM media_j
  INNER JOIN q_limit
    ON media_j.media_id = q_limit.media_id
  LIMIT 3
)
SELECT
  JSONB_PRETTY(CAST(data AS JSONB)) AS data
FROM q2