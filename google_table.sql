-- public.google_jobs definition

-- Drop table

-- DROP TABLE public.google_jobs;

CREATE TABLE public.google_jobs (
	id serial4 NOT NULL,
	url text NOT NULL,
	html_content text NULL,
	created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
	skills text NULL,
	compatibility int4 NULL,
	title text NULL,
	company_name text NULL,
	"location" text NULL,
	hasapplied int4 DEFAULT 0 NOT NULL,
	CONSTRAINT google_jobs_pkey PRIMARY KEY (id),
	CONSTRAINT url_unique UNIQUE (url)
);