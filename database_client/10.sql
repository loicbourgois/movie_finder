WITH media AS
  (SELECT item___label.label AS media,
          item___label.language AS media_language,
          item.item_id AS media_id,
          item.kind AS media_kind
   FROM item
   INNER JOIN item___label ON item.item_id = item___label.item_id
   WHERE item.kind IN ('documentary',
                       'anime',
                       'animated_television_series') ) ,
     media_director AS
  (SELECT item___label.label AS director,
          item___label.language AS director_language,
          item___director.item_id AS director_up_id,
          item___director.director_id AS director_id
   FROM item___director
   INNER JOIN item___label ON item___director.director_id = item___label.item_id) ,
     media_producer AS
  (SELECT item___label.label AS producer,
          item___label.language AS producer_language,
          item___producer.item_id AS producer_up_id,
          item___producer.producer_id AS producer_id
   FROM item___producer
   INNER JOIN item___label ON item___producer.producer_id = item___label.item_id)
SELECT DISTINCT *
FROM media
LEFT OUTER JOIN media_director ON media.media_id = media_director.director_up_id
LEFT OUTER JOIN media_producer ON media.media_id = media_producer.producer_up_id
LIMIT 3