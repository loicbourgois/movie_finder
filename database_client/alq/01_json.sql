WITH media AS (
  SELECT
    item___label.label AS media,
    item___label.language AS media_language,
    item.item_id AS media_id,
    item.kind AS media_kind
  FROM item
  INNER JOIN item___label
    ON item.item_id = item___label.item_id
  /* w1 */
  WHERE
    item.kind IN ('anime') AND TRUE
), media_genre AS (
  SELECT
    item___label.label AS media_genre,
    item___label.language AS media_genre_language,
    item___genre.item_id AS media_genre_up_id,
    item___genre.genre_id AS media_genre_id
  FROM item___genre
  INNER JOIN item___label
    ON item___genre.genre_id = item___label.item_id
  /* w2 */
  WHERE
    TRUE AND item___label.label ILIKE '%psychologie%'
), media_genre_j /* 7.2 */ AS (
  SELECT
    media_genre_up_id,
    media_genre_id,
    JSON_BUILD_OBJECT('label', JSON_OBJECT_AGG(media_genre_language, media_genre)) AS media_genre_data /* 6.2 */
  FROM media_genre
  GROUP BY
    media_genre_up_id,
    media_genre_id
), media_j AS (
  SELECT
    media_id,
    JSON_BUILD_OBJECT(
      'label',
      JSON_OBJECT_AGG(media_language, media),
      'kind',
      media.media_kind,
      'genre',
      COALESCE(
        JSON_OBJECT_AGG(media_genre_id, media_genre_data /* 6.1 */) FILTER(WHERE
          NOT media_genre_id IS NULL),
        CAST('{}' AS JSON)
      )
    ) AS media_data
  FROM media
  /* c3 */
  INNER JOIN media_genre_j
    ON media.media_id = media_genre_j.media_genre_up_id
  GROUP BY
    media.media_id,
    media.media_kind
), q_limit AS (
  SELECT DISTINCT
    media_id
  FROM media_j
  LIMIT 3
), q2 AS (
  SELECT
    JSON_OBJECT_AGG(media_j.media_id, media_j.media_data) AS data
  FROM media_j
  /* j3 */
  INNER JOIN q_limit
    ON media_j.media_id = q_limit.media_id
  LIMIT 3
)
SELECT
  JSONB_PRETTY(CAST(data AS JSONB)) AS data
FROM q2