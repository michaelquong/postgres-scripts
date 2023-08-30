-- Create the schema
CREATE SCHEMA IF NOT EXISTS entertainment;

-- Set the search path to include the "entertainment" schema
SET search_path = entertainment;

-- CREATE TYPE within the "entertainment" schema
DROP TYPE IF EXISTS entertainment.genre;
CREATE TYPE entertainment.genre AS ENUM (
    'ADVENTURE',
    'HORROR',
    'COMEDY',
    'ACTION',
    'SPORTS'
);

-- CREATE TABLE within the "entertainment" schema
DROP TABLE IF EXISTS entertainment.movies;
CREATE TABLE entertainment.movies (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    release_year SMALLINT,
    genre entertainment.genre,
    price NUMERIC(4, 2)
);


