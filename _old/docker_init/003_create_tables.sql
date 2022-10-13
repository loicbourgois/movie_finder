\connect downtowhat_rw


CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


CREATE TABLE profile (
   id uuid unique default uuid_generate_v4(),
   PRIMARY KEY( id )
);
CREATE TABLE profile_username (
  profile_id uuid unique,
  profile_username text unique not null,
  CONSTRAINT fk_profile_id
    FOREIGN KEY(profile_id)
    REFERENCES profile(id)
);
CREATE TABLE profile_hash (
  profile_id uuid unique,
  profile_hash text,
  CONSTRAINT fk_profile_id
    FOREIGN KEY(profile_id)
    REFERENCES profile(id)
);
CREATE TABLE profile_display_name (
  profile_id uuid unique,
  profile_display_name text,
  CONSTRAINT fk_profile_id
    FOREIGN KEY(profile_id)
    REFERENCES profile(id)
);
CREATE TABLE item (
  id bigint,
  PRIMARY KEY( id )
);
CREATE TABLE taste (
  profile_id uuid,
  item_id bigint,
  score int default 1000,
  CONSTRAINT fk_profile_id
    FOREIGN KEY(profile_id)
    REFERENCES profile(id),
  CONSTRAINT fk_item_id
    FOREIGN KEY(item_id)
    REFERENCES item(id)
);
CREATE TABLE subclass (
  parent_id bigint,
  child_id bigint,
  CONSTRAINT fk_parent_id
    FOREIGN KEY(parent_id)
    REFERENCES item(id),
  CONSTRAINT fk_child_id
    FOREIGN KEY(child_id)
    REFERENCES item(id)
);
CREATE TYPE language AS ENUM ('default', 'en', 'fr', 'es', 'it');
CREATE TABLE item_label (
  item_id bigint,
  language language,
  label varchar,
  CONSTRAINT fk_item_id
    FOREIGN KEY(item_id)
    REFERENCES item(id)
);
