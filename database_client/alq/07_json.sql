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
    item.kind IN ('documentary', 'film_series', 'western_animation', 'anime', 'animated_television_series')
    AND item___label.label ILIKE '%christ%'
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
), media_publication_date AS (
  SELECT
    item___label.label AS media_publication_date,
    item___label.language AS media_publication_date_language,
    item___publication_date.item_id AS media_publication_date_up_id,
    item___publication_date.publication_date_id AS media_publication_date_id
  FROM item___publication_date
  INNER JOIN item___label
    ON item___publication_date.publication_date_id = item___label.item_id
  WHERE
    TRUE
), media_publication_date_j /* 7.2 */ AS (
  SELECT
    media_publication_date_up_id,
    media_publication_date_id,
    JSON_BUILD_OBJECT('label', JSON_OBJECT_AGG(media_publication_date_language, media_publication_date)) AS media_publication_date_data /* 6.2 */
  FROM media_publication_date
  GROUP BY
    media_publication_date_up_id,
    media_publication_date_id
), media_director_j /* 7.2 */ AS (
  SELECT
    media_director_up_id,
    media_director_id,
    JSON_BUILD_OBJECT('label', JSON_OBJECT_AGG(media_director_language, media_director)) AS media_director_data /* 6.2 */
  FROM media_director
  GROUP BY
    media_director_up_id,
    media_director_id
), media_j AS (
  SELECT
    media_id,
    JSON_BUILD_OBJECT(
      'label',
      JSON_OBJECT_AGG(media_language, media),
      'kind',
      media.media_kind,
      'publication_date',
      COALESCE(
        JSON_OBJECT_AGG(media_publication_date_id, media_publication_date_data /* 6.1 */) FILTER(WHERE
          NOT media_publication_date_id IS NULL),
        CAST('{}' AS JSON)
      ),
      'director',
      COALESCE(
        JSON_OBJECT_AGG(media_director_id, media_director_data /* 6.1 */) FILTER(WHERE
          NOT media_director_id IS NULL),
        CAST('{}' AS JSON)
      )
    ) AS media_data
  FROM media
  /* c3 */
  LEFT OUTER JOIN media_publication_date_j
    ON media.media_id = media_publication_date_j.media_publication_date_up_id
  /* c3 */
  LEFT OUTER JOIN media_director_j
    ON media.media_id = media_director_j.media_director_up_id
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