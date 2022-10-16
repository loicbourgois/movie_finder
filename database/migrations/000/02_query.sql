-- CREATE DATABASE downtowhat;


\connect downtowhat;


CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


create table dtw_user (
  id uuid unique default uuid_generate_v4(),
  username text unique not null,
  email text unique not null,
  salt text not null,
  hash text not null,
  last_active timestamp without time zone default (now() at time zone('utc')),
  created_at timestamp without time zone default (now() at time zone('utc')),
  primary key( id )
);


create table tmp_user (
  id uuid unique default uuid_generate_v4(),
  last_active timestamp without time zone default (now() at time zone('utc')),
  created_at timestamp without time zone default (now() at time zone('utc')),
  primary key( id )
);


create table question (
  id uuid unique default uuid_generate_v4(),
  title text unique not null,
  prompt text not null,
  priority int unique not null,
  primary key( id )
);


create table option (
  id uuid unique default uuid_generate_v4(),
  question_id uuid not null,
  str text not null,
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
