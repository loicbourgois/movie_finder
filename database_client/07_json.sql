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
   INNER JOIN item___label ON item___director.director_id = item___label.item_id) ,
     media_publication_date_j AS
  (SELECT publication_date_up_id,
          publication_date
   FROM media_publication_date
   GROUP BY publication_date_up_id,
            publication_date) ,
     media_director_j AS
  (SELECT director_up_id,
          director_id,
          json_build_object('label', json_object_agg(director_language, director)) AS director_data
   FROM media_director
   GROUP BY director_up_id,
            director_id) ,
     media_j AS
  (SELECT media_id,
          json_build_object('label', json_object_agg(media_language, media), 'kind', media.media_kind , 'publication_date', publication_date , 'director', coalesce(json_object_agg(director_id, director_data) FILTER (
                                                                                                                                                                                                                        WHERE director_id IS NOT NULL), '{}'::JSON)) AS media_data
   FROM media
   LEFT OUTER JOIN media_publication_date_j ON media.media_id = media_publication_date_j.publication_date_up_id
   LEFT OUTER JOIN media_director_j ON media.media_id = media_director_j.director_up_id
   GROUP BY media.media_id,
            media.media_kind,
            publication_date) ,
     q_limit AS
  (SELECT DISTINCT media_id
   FROM media_j
   LIMIT 2),
     q2 AS
  (SELECT json_object_agg(media_j.media_id, media_j.media_data) AS DATA
   FROM media_j
   INNER JOIN q_limit ON media_j.media_id = q_limit.media_id
   LIMIT 3)
SELECT jsonb_pretty(DATA::JSONB) AS DATA
FROM q2;