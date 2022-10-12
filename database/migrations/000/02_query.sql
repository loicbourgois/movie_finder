CREATE DATABASE downtowhat;


\connect downtowhat;


CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


create table dtw_user (
  id uuid unique default uuid_generate_v4(),
  username text unique not null,
  email text unique not null,
  hash text not null,
  last_active timestamp,
  primary key( id )
);


create table question (
  id uuid unique default uuid_generate_v4(),
  question text not null,
  description text not null,
  primary key( id )
);


create table option (
  id uuid unique default uuid_generate_v4(),
  str text unique not null,
  priority int unique not null,
  primary key( id )
);


create table preference (
  user_id uuid,
  option_id uuid,
  score int
);


create table user_distance (
  user_a uuid,
  user_b uuid,
  distance int
);
