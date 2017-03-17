import pandas as pd

import MySQLdb

db =MySQLdb.connect(
    host='localhost',
    user='root',
    passwd='pw',
    db='brdo'
)


def init_db():
    cur = db.cursor()

    db.set_character_set('utf8')
    cur.execute('SET NAMES utf8;')
    cur.execute('SET CHARACTER SET utf8;')
    cur.execute('SET character_set_connection=utf8;')

    init_drop_tables(cur)

    init_faculty_vcr(cur)

    cur.close()

    db.commit()


def init_drop_tables(cur):
    table_sql = """
    DROP TABLE IF EXISTS faculty_webpages;

    DROP TABLE IF EXISTS faculty_vcr;

    CREATE TABLE faculty_vcr (
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

    CREATE TABLE faculty_webpages (
        faculty_name VARCHAR(50),
        faculty_webpage_content TEXT,
        PRIMARY KEY(faculty_name),
        FOREIGN KEY(faculty_name) REFERENCES faculty_vcr(faculty_name)
    );"""

    cur.execute(table_sql)


def init_faculty_vcr(cur):
    df = pd.read_csv('temp_data/faculty_vcr.csv', sep='~')

    df = df.fillna('')

    df = df.drop_duplicates('faculty_name')

    df['faculty_name'] = df['faculty_name'].apply(lambda s:s.lower())

    rows = []

    for row in df.iterrows():
        rows.append(row[1].values.tolist())

    sql = """INSERT INTO faculty_vcr VALUES (""" + (" %s," * (len(df.columns.values) - 1)) + """ %s )"""

    cur.executemany(sql, rows)




init_db()