ALTER TABLE item ADD CONSTRAINT pk___item PRIMARY KEY (item_id, kind);
ALTER TABLE item___label ADD CONSTRAINT pk___item___label PRIMARY KEY (item_id, language, label);
ALTER TABLE item___director ADD CONSTRAINT pk___item___director PRIMARY KEY (item_id, director_id);
ALTER TABLE item___creator ADD CONSTRAINT pk___item___creator PRIMARY KEY (item_id, creator_id);


CREATE INDEX index___item___item_id ON item (item_id);
CREATE INDEX index___item___kind ON item (kind);
CREATE INDEX index___item___label___item_id ON item___label (item_id);
CREATE INDEX index___item___label___language ON item___label (language);
CREATE INDEX index___item___label___label ON item___label (label);
CREATE INDEX index___item___director___item_id ON item___director (item_id);
CREATE INDEX index___item___director___kind ON item___director (director_id);



CREATE INDEX item___label___idx_01 ON item___label (item_id, language);
CREATE INDEX item___label___idx_02 ON item___label (language, item_id);
CREATE INDEX item___label___idx_03 ON item___label (item_id, label);
CREATE INDEX item___label___idx_04 ON item___label (label, item_id);
CREATE INDEX item___label___idx_05 ON item___label (language, label);
CREATE INDEX item___label___idx_06 ON item___label (label, language);
