CREATE DATABASE IF NOT EXISTS brdo;

DROP TABLE IF EXISTS brdo.faculty_webpages;

DROP TABLE IF EXISTS brdo.faculty_vcr;

DROP TABLE IF EXISTS brdo.grants;

CREATE TABLE brdo.faculty_vcr (
    faculty_name VARCHAR(50) NOT NULL,
    faculty_profile_url VARCHAR(200),
    l_expertise TEXT,
    department VARCHAR(50),
    title_name VARCHAR(200),
    faculty_site_url VARCHAR(500),
    lab_url VARCHAR(500),
    faculty_email VARCHAR(50),
    description TEXT,
    description_links TEXT,
    article_date_1 DATE,
    title_of_news_1 VARCHAR(500),
    link_to_news_1 VARCHAR(500),
    description_teaser_1 TEXT,
    article_date_2 DATE,
    title_of_news_2 VARCHAR(500),
    link_to_news_2 VARCHAR(500),
    description_teaser_2 TEXT,
    article_date_3 DATE,
    title_of_news_3 VARCHAR(500),
    link_to_news_3 VARCHAR(500),
    description_teaser_3 TEXT,
    article_date_4 DATE,
    title_of_news_4 VARCHAR(500),
    link_to_news_4 VARCHAR(500),
    description_teaser_4 TEXT,
    article_date_5 DATE,
    title_of_news_5 VARCHAR(500),
    link_to_news_5 VARCHAR(500),
    description_teaser_5 TEXT,
    PRIMARY KEY(faculty_name) /* better hope the faculty_names are unique, we will find out*/
);

CREATE TABLE brdo.faculty_webpages (
    faculty_name VARCHAR(50),
    faculty_webpage_content TEXT,
    PRIMARY KEY(faculty_name),
    FOREIGN KEY(faculty_name) REFERENCES brdo.faculty_vcr(faculty_name)
);

CREATE TABLE brdo.grants (
    grant_name TEXT,
    grant_description TEXT,
    date_inserted_into_db DATE
)