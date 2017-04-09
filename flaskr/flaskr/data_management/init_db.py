import pandas as pd

# from flaskr.flaskr.data_management.format_grant_data_sources import *

from format_grant_data_sources import *

import MySQLdb

db =MySQLdb.connect(
    host='127.0.0.1',
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

    init_drop_and_create_tables(cur)

    init_faculty_vcr(cur)

    init_faculty_webpages(cur)

    init_grants(cur)

    db.commit()


def init_drop_and_create_tables(cur):
    """
    Drops tables, then creates tables in the database to which the cursor originates from
    :param cur: Cursor object
    :return:
    """
    cur.execute("""DROP TABLE IF EXISTS faculty_webpages;""")
    cur.execute("""DROP TABLE IF EXISTS faculty_vcr;""")
    cur.execute("""DROP TABLE IF EXISTS grants;""")
    cur.execute("""DROP TABLE IF EXISTS grants_user_input;""")
    cur.execute("""CREATE TABLE faculty_vcr (
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
        );""")
    cur.execute("""CREATE TABLE faculty_webpages (
            faculty_name VARCHAR(50),
            faculty_webpage_url TEXT,
            faculty_webpage_content TEXT,
            PRIMARY KEY(faculty_name),
            FOREIGN KEY(faculty_name) REFERENCES faculty_vcr(faculty_name)
        );""")


    # Create index to speed up lookup/WHERE (no large text data on page, just keys which are names)
    cur.execute("""CREATE INDEX faculty_webpages_index ON faculty_webpages (faculty_name);""")

    cur.execute("""CREATE TABLE grants (
            grant_title VARCHAR(500),
            grant_description TEXT,
            grant_posted_date VARCHAR(10),
            grant_closing_date VARCHAR(10),
            grant_info_url VARCHAR(80),
            grant_sponsor TEXT,
            grant_award_floor TEXT,
            grant_award_ceiling TEXT,
            grant_db_insert_date VARCHAR(10),
            PRIMARY KEY(grant_title, grant_info_url)
        );""")

    cur.execute("""CREATE INDEX grants_index ON grants (grant_db_insert_date);""")

    cur.execute("""CREATE TABLE grants_user_input (
                grant_title VARCHAR(500),
                grant_description TEXT,
                grant_posted_date DATE,
                grant_closing_date DATE,
                grant_info_url VARCHAR(80),
                grant_sponsor TEXT,
                grant_award_floor TEXT,
                grant_award_ceiling TEXT,
                grant_db_insert_date DATE,
                PRIMARY KEY(grant_title, grant_info_url)
            );""")


def split_first_last_name(s):
    """
    Find highest two 'words', those are the first and last name by order
    """
    l = s.lower().split(' ')
    lengths = [len(w) for w in l]
    max_index = max(range(len(l)), key=lambda i: lengths[i])
    max_word = l[max_index]
    lengths[max_index] = -1

    max_index2 = max(range(len(l)), key=lambda i: lengths[i])
    max_word2 = l[max_index2]

    if max_index < max_index2:
        return max_word, max_word2
    else:
        return max_word2, max_word

def init_faculty_vcr(cur):
    df = pd.read_csv('temp_data/faculty_vcr.csv', sep='~')

    # df = df.fillna('')
    df = df.where(pd.notnull(df), None)

    first_last_names = df['faculty_name'].apply(split_first_last_name)
    first_names = [t[0] for t in first_last_names]
    last_names = [t[1] for t in first_last_names]
    df['faculty_name'] = [first_name + ' ' + last_name for first_name, last_name in zip(first_names, last_names)]

    df['faculty_name'] = df['faculty_name'].apply(lambda s:s.lower())

    df = df.drop_duplicates('faculty_name')

    rows = []

    for row in df.iterrows():
        rows.append(row[1].values.tolist())

    sql = """INSERT INTO faculty_vcr VALUES (""" + (" %s," * (len(df.columns.values) - 1)) + """ %s )"""

    cur.executemany(sql, rows)

def init_faculty_webpages(cur):
    df = pd.read_csv('temp_data/complete_cleaned_faculty_webpages.csv')

    # df = df.fillna('')
    df = df.where(pd.notnull(df), None)

    df = df.drop_duplicates('full_name')

    df['full_name'] = df['full_name'].apply(lambda s: s.lower())

    rows = []

    for row in df.iterrows():
        rows.append(row[1].values.tolist())

    sql = """INSERT INTO faculty_webpages VALUES (""" + (" %s," * (len(df.columns.values) - 1)) + """ %s )"""

    cur.executemany(sql, rows)

def init_grants(cur):
    grants_db_column_names = [
        'grant_title',
        'grant_description',
        'grant_posted_date',
        'grant_closing_date',
        'grant_info_url',
        'grant_sponsor',
        'grant_award_floor',
        'grant_award_ceiling',
        'grant_db_insert_date'
    ]

    sql = """INSERT INTO grants VALUES (""" + (" %s," * (len(grants_db_column_names) - 1)) + """ %s )"""

    #get data sources data
    #combine into one big list
    #insert many

    # grants.gov
    grants_gov_df = format_grants_gov_data()

    grants_gov_df = grants_gov_df.drop_duplicates(['grant_title', 'grant_info_url'])

    rows = []
    for row in grants_gov_df.iterrows():
        rows.append(row[1].values.tolist())

    cur.executemany(sql, rows)


init_db()
