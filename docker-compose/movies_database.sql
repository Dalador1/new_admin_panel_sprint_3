CREATE SCHEMA IF NOT EXISTS content;

CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    rating REAL,
    type TEXT NOT NULL,
    file_path TEXT,
    created timestamp with time zone,
    modified timestamp with time zone 
);

CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created timestamp with time zone,
    modified timestamp with time zone 
);

CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    genre_id UUID NOT NULL,
    film_work_id UUID NOT NULL,    
    created timestamp with time zone,
    modified timestamp with time zone,

    FOREIGN KEY (genre_id) REFERENCES content.genre(id) ON DELETE CASCADE,
    FOREIGN KEY (film_work_id) REFERENCES content.film_work(id) ON DELETE CASCADE 
);

CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone 
);

CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY, 
    person_id UUID NOT NULL,
    film_work_id UUID NOT NULL,
    role TEXT NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone,
    FOREIGN KEY (person_id) REFERENCES content.person(id) ON DELETE CASCADE, 
    FOREIGN KEY (film_work_id) REFERENCES content.film_work(id) ON DELETE CASCADE 
);

CREATE INDEX IF NOT EXISTS film_title_idx ON content.film_work (title, type);
CREATE UNIQUE INDEX IF NOT EXISTS genre_name_idx ON content.genre(name);
CREATE UNIQUE INDEX IF NOT EXISTS person_full_name_idx ON content.person(full_name);
CREATE UNIQUE INDEX IF NOT EXISTS person_film_work_person_id_film_work_id_idx ON content.person_film_work(person_id, film_work_id, role);
CREATE UNIQUE INDEX IF NOT EXISTS genre_film_work_genre_id_film_work_id_idx ON content.genre_film_work(genre_id, film_work_id);

CREATE EXTENSION IF NOT EXISTS wal2json;
SELECT pg_create_logical_replication_slot('my_slot', 'wal2json');