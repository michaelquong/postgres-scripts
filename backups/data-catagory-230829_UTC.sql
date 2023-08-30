PGDMP         ;                {           catagory    9.6.24     14.9 (Ubuntu 14.9-1.pgdg20.04+1)     V           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            W           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            X           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            Y           1262    16384    catagory    DATABASE     \   CREATE DATABASE catagory WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'en_US.utf8';
    DROP DATABASE catagory;
                postgres    false                        2615    16385    entertainment    SCHEMA        CREATE SCHEMA entertainment;
    DROP SCHEMA entertainment;
                postgres    false            �           1247    16387    genre    TYPE     u   CREATE TYPE entertainment.genre AS ENUM (
    'ADVENTURE',
    'HORROR',
    'COMEDY',
    'ACTION',
    'SPORTS'
);
    DROP TYPE entertainment.genre;
       entertainment          postgres    false    8            �            1259    16399    movies    TABLE     �   CREATE TABLE entertainment.movies (
    id integer NOT NULL,
    title character varying NOT NULL,
    release_year smallint,
    genre entertainment.genre,
    price numeric(4,2)
);
 !   DROP TABLE entertainment.movies;
       entertainment            postgres    false    480    8            �            1259    16397    movies_id_seq    SEQUENCE     }   CREATE SEQUENCE entertainment.movies_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE entertainment.movies_id_seq;
       entertainment          postgres    false    187    8            Z           0    0    movies_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE entertainment.movies_id_seq OWNED BY entertainment.movies.id;
          entertainment          postgres    false    186            �           2604    16402 	   movies id    DEFAULT     t   ALTER TABLE ONLY entertainment.movies ALTER COLUMN id SET DEFAULT nextval('entertainment.movies_id_seq'::regclass);
 ?   ALTER TABLE entertainment.movies ALTER COLUMN id DROP DEFAULT;
       entertainment          postgres    false    187    186    187            S          0    16399    movies 
   TABLE DATA           N   COPY entertainment.movies (id, title, release_year, genre, price) FROM stdin;
    entertainment          postgres    false    187   �       [           0    0    movies_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('entertainment.movies_id_seq', 1, false);
          entertainment          postgres    false    186            �           2606    16407    movies movies_pkey 
   CONSTRAINT     W   ALTER TABLE ONLY entertainment.movies
    ADD CONSTRAINT movies_pkey PRIMARY KEY (id);
 C   ALTER TABLE ONLY entertainment.movies DROP CONSTRAINT movies_pkey;
       entertainment            postgres    false    187            S   �   x�]��n� E��W0u� �$�V�(��`a7R�.�Au"�U��H���{�y���~��x��ae.�������TJ*�u!b�؀�#T@�=���U��L*a����$$Y��U�9k6~�=yh�o����:���h�a"�(��TCu��Й`<� ��
D`b�	�uˌWIt�fx�G(y�\�^{��;bY*"�e/�����s��C,�^ �~d�P�     