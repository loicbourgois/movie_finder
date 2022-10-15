BEGIN;


-- insert into tmp_user default values;

select * from tmp_user;


-- CREATE OR REPLACE FUNCTION max_answers_inner (
--   total_ bigint,
--   next_ bigint
-- ) returns table (
--   total bigint,
--   next bigint
-- ) AS $$
-- BEGIN
--   IF next_ > 0 THEN
--     return query
--     select * from max_answers_inner(total_+next_, next_-1);
--   else
--     return query
--     select total_, next_;
--   END IF;
-- END;
-- $$ LANGUAGE plpgsql;
--
--
-- CREATE OR REPLACE FUNCTION max_answers (
--   x bigint
-- ) returns table (
--   y bigint
-- ) AS $$
-- BEGIN
--   return query
--   select total from max_answers_inner(x-1, x-2);
-- END;
-- $$ LANGUAGE plpgsql;



-- CREATE OR REPLACE FUNCTION progress (
--   answer_count bigint,
--   rounds bigint
-- ) returns table (
--   progress float
-- ) AS $$
-- BEGIN
--   return query
--   select 1.0::float;
--   -- select ((answer_count / rounds) as float);
-- END;
-- $$ LANGUAGE plpgsql;
--
--
-- CREATE OR REPLACE FUNCTION priority_x_remaining (
--   prio_max int,
--   priority int,
--   progress float
-- ) returns table (
--   priority_x_remaining float
-- ) AS $$
-- BEGIN
--   return query
--   select 1.0::float;
-- END;
-- $$ LANGUAGE plpgsql;




with prio_max as (
  select max(priority) as prio_max
  from question
),
q1 as (
select
  question.prompt,
  question.priority,
  tmp_user.id as tmp_user_id,
  (
    select count(*)
    from tmp_answer
    where question_id = question.id
      and tmp_answer.tmp_user_id = tmp_user.id
  ) as answer_count,
  (
    select count(*)
    from option
    where question.id = option.question_id
  ) as option_count
  from question, tmp_user
),
q2 as (
          select *
          from q1, prio_max
      ),
      q3 as (
          select *, ((option_count)*(option_count-1)/2) as rounds
          from q2
      ),
      q4 as (
          select *, cast(answer_count as float) / cast(rounds as float) as progress
          from q3
      ),
      q5 as (
          select *, cast( (prio_max+1-priority) as float) * (1.0  - progress ) as priority_x_remaining
          from q4
      ),
      Q as (
          select * from q5
      )
select *
from Q;


rollback;
