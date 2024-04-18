WITH media AS
  (SELECT item___label.label AS media,
          item___label.language AS media_language,
          item.item_id AS media_id,
          item.kind AS media_kind
   FROM item
   INNER JOIN item___label ON item.item_id = item___label.item_id
   WHERE item.kind IN ('documentary',
                       'film_series',
                       'western_animation',
                       'anime',
                       'animated_television_series') ) ,
     media_publication_date AS
  (SELECT item___publication_date.item_id AS publication_date_up_id,
          item___publication_date.publication_date AS publication_date
   FROM item___publication_date) ,
     media_director AS
  (SELECT item___label.label AS director,
          item___label.language AS director_language,
          item___director.item_id AS director_up_id,
          item___director.director_id AS director_id
   FROM item___director
   INNER JOIN item___label ON item___director.director_id = item___label.item_id)
SELECT DISTINCT *
FROM media
LEFT OUTER JOIN media_publication_date ON media.media_id = media_publication_date.publication_date_up_id
LEFT OUTER JOIN media_director ON media.media_id = media_director.director_up_id
LIMIT 2