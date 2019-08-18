DROP TABLE IF EXISTS knownfiles;
CREATE TABLE knownfiles (
	full_path TEXT NOT NULL,
	record_source TEXT,
	content_md5 TEXT,
	last_accessed TIMESTAMP,
	last_seen TIMESTAMP
);
ALTER TABLE knownfiles OWNER TO lutz;
ALTER TABLE ONLY knownfiles ADD CONSTRAINT "PKEY_KNOWNFILES" PRIMARY KEY (full_path,record_source);
