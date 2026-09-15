-- =====================================================================
-- schema.sql
-- HIST 8510  ·  Week 2 mini-assignment
--
-- YOUR NAME: Sharon Dorsey
-- YOUR SOURCES (one line — what are they, roughly how many, what years): 89 records from the SC WPA Church Records Survey from 1936
--
--
-- Write your schema here. Look at 01_create_schema.sql in the week folder
-- for a worked example, but do not just rename its tables. Your sources
-- are not Damron's guidebooks and they will not want the same shape.
--
-- Requirements for Wednesday:
--   · at least three tables
--   · at least one genuine many-to-many, modeled with a junction table
--   · comments explaining WHY, not just what
--
-- Run it with build_db.py, or open it in DBcode and run one statement
-- at a time.
-- =====================================================================


-- Start clean, in reverse order of creation. You cannot drop a table
-- that another table still points at.
DROP TABLE IF EXISTS church_pastor;
DROP TABLE IF EXISTS church;
DROP TABLE IF EXISTS people;
DROP TABLE IF EXISTS city;

-- Specifically designed to delete the tables for teaching purposes; throw away the previous structure and create a brand new one
-- if you have an app running on top of this and you change something in the app, drop table will overwrite anything in the app
-- if you do everything on excel and import, you may want to keep this
-- in MGG, they don't have these because they have a live database on the internet. They have a sequel script that they individually edit each time so it's not rewritten every time.

-- ---------------------------------------------------------------------
-- Table 1 — probably your lookup or "one" side
-- ---------------------------------------------------------------------
-- Ask yourself: what value is repeated over and over in my flat notes?
-- That repetition usually means an entity you have not pulled out yet.

 CREATE TABLE city (
    city_id    INTEGER PRIMARY KEY,
    city_name TEXT NOT NULL,
    county TEXT NOT NULL,
    state TEXT NOT NULL
 );


-- ---------------------------------------------------------------------
-- Table 2 — your central table, the thing you have the most rows of
-- ---------------------------------------------------------------------
-- Two things to decide here, and to write down in a comment:
--
--   1. What is ONE ROW? Be exact. "One petition" and "one signature on a
--      petition" are different databases.
--
--   2. Is there a field in your sources stable enough to be a natural
--      key? Usually not. Use a surrogate integer and keep the source's
--      own identifier as an ordinary column so you can get back to the
--      document.
--
CREATE TABLE church (
     church_id    INTEGER PRIMARY KEY,
     name_of_church       TEXT NOT NULL,
     year_organized INTEGER NOT NULL,
     county TEXT NOT NULL,
     -- The WPA survey left these blank for roughly half the churches, so
     -- they are nullable: a missing value is real information, not a zero.
     denomination TEXT NOT NULL,
     property_value INTEGER,
     present_membership INTEGER,
     charter_membership INTEGER,
     city_id    INTEGER NOT NULL,      -- foreign key goes on the many side
     FOREIGN KEY (city_id) REFERENCES city (city_id)
 );


-- add county to location table with city and state


-- Table 3: Pastor table

CREATE TABLE people (
    people_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    years_active TEXT NOT NULL
);
-- people table and connect the people to the church - can include surveyors and type (mill owner, surveyor, minister)
-- another many to many
-- ---------------------------------------------------------------------
-- Table 4 — the junction table
-- ---------------------------------------------------------------------
-- This is the one people skip, and it is the one Wednesday is for.
--
-- You need it whenever a thing can have several of something AND that
-- something describes several things. Multiple authors on a document.
-- Multiple topics on a petition. Multiple people at an event.
--
-- If you find yourself wanting a column called topic_1, topic_2,
-- topic_3, or a single column holding "war, pensions, land" with commas
-- in it, that is a many-to-many asking for a junction table.
--
CREATE TABLE church_people (
    church_id    INTEGER NOT NULL,
    people_id    INTEGER NOT NULL,
    PRIMARY KEY (church_id, people_id),
    FOREIGN KEY (church_id) REFERENCES church (church_id),
    FOREIGN KEY (people_id) REFERENCES people (people_id)
);


-- =====================================================================
-- Remember: PRAGMA foreign_keys = ON has to be set on every connection.
-- The FOREIGN KEY lines above do nothing without it. build_db.py sets it.
-- =====================================================================
