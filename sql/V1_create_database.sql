CREATE TABLE users (
	id           SERIAL NOT NULL,
	login        VARCHAR(200),
	passwordHash VARCHAR(32),
	apiKey       VARCHAR(60),
	PRIMARY KEY (id)
);

CREATE TABLE emails (
	id         SERIAL NOT NULL,
	user_id    INTEGER,
	from_email VARCHAR(254),
	recipients VARCHAR,
	subject    VARCHAR(100),
	html       VARCHAR,
	created_at BIGINT,
	status     SMALLINT,
	updated_at BIGINT,
	via        VARCHAR(100),
	message    VARCHAR,
	PRIMARY KEY (id),
	FOREIGN KEY(user_id) REFERENCES users (id)
);

create extension "uuid-ossp";