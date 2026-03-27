select 'Number of items with "Titanic" in the title (case sensitive)' as about;
select count(*)
from item___label
where label like '%Titanic%';
