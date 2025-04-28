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
), media_cast_member AS (
  SELECT
    item___label.label AS media_cast_member,
    item___label.language AS media_cast_member_language,
    item___cast_member.item_id AS media_cast_member_up_id,
    item___cast_member.cast_member_id AS media_cast_member_id
  FROM item___cast_member
  INNER JOIN item___label
    ON item___cast_member.cast_member_id = item___label.item_id
  /* w2 */
  WHERE
    TRUE
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
), q_all AS (
  SELECT DISTINCT
    *
  FROM media
  LEFT OUTER JOIN media_cast_member
    ON media.media_id = media_cast_member.media_cast_member_up_id
  LEFT OUTER JOIN media_genre
    ON media.media_id = media_genre.media_genre_up_id
  WHERE
    TRUE AND media_genre ILIKE '%psychologie%'
), q_limit AS (
  SELECT DISTINCT
    media_id
  FROM q_all
  LIMIT 3
)
SELECT
  q_all.*
FROM q_all
INNER JOIN q_limit
  ON q_all.media_id = q_limit.media_id