\d

WITH q1 as (
  select 
    item_id,
    max(review_score) as review_score_max,
    avg(review_score) as review_score_avg,
    count(review_score) as review_score_count
  from item___review_score
  group by item_id
)
, q2 as (
  select 
    q1.* ,
    'https://www.imdb.com/title/' || imdb_id as imdb_link
  from q1 
  left outer join item___imdb_id as b
  on q1.item_id = b.item_id
)
, q3 as (
  select 
    q2.*
  from q2
  order by review_score_count desc, review_score_avg desc
  limit 100
)
select * from q3;