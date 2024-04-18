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
    item.kind IN ('documentary', 'anime', 'animated_television_series')
), media_producer AS (
  SELECT
    item___label.label AS media_producer,
    item___label.language AS media_producer_language,
    item___producer.item_id AS media_producer_up_id,
    item___producer.producer_id AS media_producer_id
  FROM item___producer
  INNER JOIN item___label
    ON item___producer.producer_id = item___label.item_id
  WHERE
    TRUE
), media_producer_gender AS (
  SELECT
    item___label.label AS media_producer_gender,
    item___label.language AS media_producer_gender_language,
    item___gender.item_id AS media_producer_gender_up_id,
    item___gender.gender_id AS media_producer_gender_id
  FROM item___gender
  INNER JOIN item___label
    ON item___gender.gender_id = item___label.item_id
  WHERE
    TRUE
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
), media_director_gender_j /* 7.2 */ AS (
  SELECT
    media_director_gender_up_id,
    media_director_gender_id,
    JSON_BUILD_OBJECT('label', JSON_OBJECT_AGG(media_director_gender_language, media_director_gender)) AS media_director_gender_data /* 6.2 */
  FROM media_director_gender
  GROUP BY
    media_director_gender_up_id,
    media_director_gender_id
), media_director_j /* 7.2 */ AS (
  SELECT
    media_director_up_id,
    media_director_id,
    JSON_BUILD_OBJECT(
      'label',
      JSON_OBJECT_AGG(media_director_language, media_director),
      'gender',
      COALESCE(
        JSON_OBJECT_AGG(media_director_gender_id, media_director_gender_data /* 6.1 */) FILTER(WHERE
          NOT media_director_gender_id IS NULL),
        CAST('{}' AS JSON)
      )
    ) AS media_director_data /* 6.2 */
  FROM media_director
  /* c4 */
  LEFT OUTER JOIN media_director_gender_j /* 7.1 */
    ON media_director.media_director_id = media_director_gender_j.media_director_gender_up_id
  GROUP BY
    media_director_up_id,
    media_director_id
), media_producer_gender_j /* 7.2 */ AS (
  SELECT
    media_producer_gender_up_id,
    media_producer_gender_id,
    JSON_BUILD_OBJECT('label', JSON_OBJECT_AGG(media_producer_gender_language, media_producer_gender)) AS media_producer_gender_data /* 6.2 */
  FROM media_producer_gender
  GROUP BY
    media_producer_gender_up_id,
    media_producer_gender_id
), media_producer_j /* 7.2 */ AS (
  SELECT
    media_producer_up_id,
    media_producer_id,
    JSON_BUILD_OBJECT(
      'label',
      JSON_OBJECT_AGG(media_producer_language, media_producer),
      'gender',
      COALESCE(
        JSON_OBJECT_AGG(media_producer_gender_id, media_producer_gender_data /* 6.1 */) FILTER(WHERE
          NOT media_producer_gender_id IS NULL),
        CAST('{}' AS JSON)
      )
    ) AS media_producer_data /* 6.2 */
  FROM media_producer
  /* c4 */
  LEFT OUTER JOIN media_producer_gender_j /* 7.1 */
    ON media_producer.media_producer_id = media_producer_gender_j.media_producer_gender_up_id
  GROUP BY
    media_producer_up_id,
    media_producer_id
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
        JSON_OBJECT_AGG(media_director_id, media_director_data /* 6.1 */) FILTER(WHERE
          NOT media_director_id IS NULL),
        CAST('{}' AS JSON)
      ),
      'producer',
      COALESCE(
        JSON_OBJECT_AGG(media_producer_id, media_producer_data /* 6.1 */) FILTER(WHERE
          NOT media_producer_id IS NULL),
        CAST('{}' AS JSON)
      )
    ) AS media_data
  FROM media
  /* c3 */
  LEFT OUTER JOIN media_director_j
    ON media.media_id = media_director_j.media_director_up_id
  /* c3 */
  LEFT OUTER JOIN media_producer_j
    ON media.media_id = media_producer_j.media_producer_up_id
  GROUP BY
    media.media_id,
    media.media_kind
), q_limit AS (
  SELECT DISTINCT
    media_id
  FROM media_j
  LIMIT 1
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