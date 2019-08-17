DROP TABLE IF EXISTS knownfiles;
CREATE TABLE knownfiles (
	full_path TEXT NOT NULL,
	record_source TEXT,
	content_md5 TEXT,
	last_seen TIMESTAMP
);
ALTER TABLE knownfiles OWNER TO lutz;
ALTER TABLE ONLY knownfiles ADD CONSTRAINT "PKEY_KNOWNFILES" PRIMARY KEY (full_path,record_source);

DROP TABLE IF EXISTS skip_directories;
CREATE TABLE skip_directories (
	full_path TEXT NOT NULL
);
ALTER TABLE skip_directories OWNER TO lutz;
ALTER TABLE ONLY skip_directories ADD CONSTRAINT "PKEY_SKIP" PRIMARY KEY (full_path);
INSERT INTO skip_directories  VALUES 
('/home/lutz/.cache')
;
