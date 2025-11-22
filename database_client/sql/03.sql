select 'Number of items with "horizon" in the title (case insensitive)' as about;
select count(*)
from item___label
where lower(label) like '%horizon%';
