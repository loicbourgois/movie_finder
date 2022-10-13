-- This file is generated
-- Do not edit
\connect downtowhat_rw

ALTER TABLE profile ADD COLUMN sys_period tstzrange NOT NULL DEFAULT tstzrange(current_timestamp, null);
CREATE TABLE profile_history (LIKE profile);
CREATE TRIGGER profile_versioning_trigger BEFORE INSERT OR UPDATE OR DELETE ON profile
  FOR EACH ROW EXECUTE PROCEDURE versioning('sys_period', 'profile_history', true);
