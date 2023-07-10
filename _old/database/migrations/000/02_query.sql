-- CREATE DATABASE downtowhat;


\connect downtowhat;


CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


create table dtw_user (
  id uuid unique default uuid_generate_v4(),
  username varchar(128) unique not null,
  email varchar(128) unique not null,
  salt varchar(128) not null,
  hash varchar(128) not null,
  description varchar(1024) not null default '',
  birthday date default '2000/01/01',
  picture_1 bytea,
  picture_1_status varchar(128),
  picture_2 bytea,
  picture_2_status varchar(128),
  picture_3 bytea,
  picture_3_status varchar(128),
  picture_4 bytea,
  picture_4_status varchar(128),
  last_active timestamp without time zone default (now() at time zone('utc')),
  created_at timestamp without time zone default (now() at time zone('utc')),
  primary key( id )
);


alter table dtw_user
   add constraint check_picture_1_length
   check (octet_length(picture_1) <= 1024 * 8 * 2);
alter table dtw_user
  add constraint check_picture_2_length
  check (octet_length(picture_2) <= 1024 * 8 * 2);
alter table dtw_user
   add constraint check_picture_3_length
   check (octet_length(picture_3) <= 1024 * 8 * 2);
alter table dtw_user
  add constraint check_picture_4_length
  check (octet_length(picture_4) <= 1024 * 8 * 2);


create table tmp_user (
  id uuid unique default uuid_generate_v4(),
  share_id uuid unique default uuid_generate_v4(),
  pseudo varchar(128) not null default 'Anon',
  last_active timestamp without time zone default (now() at time zone('utc')),
  created_at timestamp without time zone default (now() at time zone('utc')),
  primary key( id )
);


create table question (
  id uuid unique default uuid_generate_v4(),
  title varchar(128) unique not null,
  prompt varchar(128) not null,
  priority int unique not null,
  primary key( id )
);


create table option (
  id uuid unique default uuid_generate_v4(),
  question_id uuid not null,
  str varchar(128) not null,
  primary key( id ),
  foreign key ( question_id ) references question(id),
  UNIQUE(question_id, id)
);


create table tmp_answer (
  tmp_user_id uuid not null,
  question_id uuid not null,
  option_a uuid not null,
  option_b uuid not null,
  option_win uuid not null,
  option_lose uuid not null,
  created_at timestamp without time zone default (now() at time zone('utc')),
  primary key( tmp_user_id, option_a, option_b ),
  foreign key ( question_id ) references question(id),
  foreign key ( option_a ) references option(id),
  foreign key ( option_b ) references option(id),
  foreign key ( option_win ) references option(id),
  foreign key ( option_lose ) references option(id),
  foreign key ( question_id, option_a ) references option(question_id, id),
  foreign key ( question_id, option_b ) references option(question_id, id)
);


create table answer (
  user_id uuid not null,
  question_id uuid not null,
  option_a uuid not null,
  option_b uuid not null,
  option_win uuid not null,
  option_lose uuid not null,
  created_at timestamp without time zone default (now() at time zone('utc')),
  primary key( user_id, option_a, option_b ),
  foreign key ( question_id ) references question(id),
  foreign key ( option_a ) references option(id),
  foreign key ( option_b ) references option(id),
  foreign key ( option_win ) references option(id),
  foreign key ( option_lose ) references option(id),
  foreign key ( question_id, option_a ) references option(question_id, id),
  foreign key ( question_id, option_b ) references option(question_id, id)
);


create table user_distance (
  user_a uuid,
  user_b uuid,
  distance int
);
