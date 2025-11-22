select 'Number of items per language' as about;
select
    language
    , count(*) as item_count
from item___label
group by language;
