BEGIN;


select * from tmp_user;


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
          select *, cast( (prio_max+1-priority) as float) * (1.0  - progress ) * (1.0  - progress ) as priority_x_remaining
          from q4
      ),
      Q as (
          select * from q5
      )
select * from Q;



with q1 as (
  select
    t_a.tmp_user_id as ua,
    t_b.tmp_user_id as ub,
    t_a.option_a,
    t_a.option_b,
    t_a.option_win = t_b.option_win as same
  from
    tmp_answer t_a,
    tmp_answer t_b
  where
    t_a.tmp_user_id < t_b.tmp_user_id
    and t_a.option_a = t_b.option_a
    and t_a.option_b = t_b.option_b
),
q2 as (
  select count(same)as total , ua, ub  from q1 group by ua, ub
),
q3 as (
  select count(same)as same, ua, ub,
  ( select count(*) from tmp_answer where tmp_user_id = ua ) as total_a,
  ( select count(*) from tmp_answer where tmp_user_id = ub ) as total_b
  from q1 where same group by ua, ub
)

select
  q2.ua, q2.ub,
  total_a,
  total_b,
  total as total_ab,
  same,
  cast(same as float) * 2.0 / cast(total_a + total_b as float) as match
from q2, q3
where q2.ua = q3.ua
  and q2.ub = q3.ub
  and (
    q2.ua = '8847343f-9e1c-461d-9a20-262165d98f8b'
    or q2.ub = '8847343f-9e1c-461d-9a20-262165d98f8b'
  )
group by total, same, q2.ua, q2.ub, q3.total_a, q3.total_b
order by match desc
limit 9 ;



rollback;
