from collections import defaultdict
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import nltk.stem.wordnet as wordnet
import numpy as np
import pickle
import random
import sklearn
import string
import time

import pandas as pd

from format_grant_data_sources import *

import MySQLdb


"""
Requires the following in data_management/temp_data/
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
faculty_vcr.csv
complete_cleaned_faculty_webpages.csv
grants_gov.csv
research_grant_history.csv
bids_data.csv
nsf.csv
usda.csv
"""

db =MySQLdb.connect(
    host='127.0.0.1',
    user='root',
    passwd='pw',
    db='brdo'
)


def init_db(inserting_grants=True):
    cur = db.cursor()

    db.set_character_set('utf8')
    cur.execute('SET NAMES utf8;')
    cur.execute('SET CHARACTER SET utf8;')
    cur.execute('SET character_set_connection=utf8;')

    if inserting_grants:
        init_drop_and_create_tables(cur)

        init_faculty_vcr(cur)

        init_faculty_webpages(cur)

    init_grants(cur)

    if inserting_grants:
        init_faculty_previous_grants(cur)

        create_vectorizers()

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
    cur.execute("""DROP TABLE IF EXISTS faculty_grants;""")
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
            grant_info_url VARCHAR(100),
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
                grant_info_url VARCHAR(100),
                grant_sponsor TEXT,
                grant_award_floor TEXT,
                grant_award_ceiling TEXT,
                grant_db_insert_date DATE,
                PRIMARY KEY(grant_title, grant_info_url)
            );""")

    cur.execute("""CREATE TABLE faculty_grants (
                    title TEXT,
                    faculty TEXT
                );""")

def init_faculty_vcr(cur):
    """
    Reads 'faculty_vcr.csv' from temp_data and inserts it into table faculty_vcr
    :param cur:
    :return:
    """
    df = pd.read_csv('temp_data/faculty_vcr.csv', sep='~')

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
    """
    Reads 'complete_cleaned_faculty_weboages.csv' from temp_data and inserts it into table faculty_webpages
    :param cur:
    :return:
    """
    df = pd.read_csv('temp_data/complete_cleaned_faculty_webpages.csv')

    df = df.where(pd.notnull(df), None)

    df = df.drop_duplicates('full_name')

    df['full_name'] = df['full_name'].apply(lambda s: s.lower())

    rows = []

    for row in df.iterrows():
        rows.append(row[1].values.tolist())

    sql = """INSERT INTO faculty_webpages VALUES (""" + (" %s," * (len(df.columns.values) - 1)) + """ %s )"""

    cur.executemany(sql, rows)

def init_grants(cur):
    """
    Reads all of the grant csv files from temp_data and inserts/updates them into grants
        -grants.gov
        -nsf
    :param cur:
    :return:
    """
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

    # don't update the grant_db_insert_date because we want the initial insert date
    update_sql = ', '.join(['`{}`=VALUES(`{}`)'.format(col, col) for col in grants_db_column_names[:-1]])

    insert_on_duplicate_update_sql = """INSERT INTO grants VALUES (""" + (" %s," * (len(grants_db_column_names) - 1)) + """ %s )
            ON DUPLICATE KEY UPDATE """ + update_sql

    # grants.gov
    grants_gov_df = format_grants_gov_data()

    # nsf
    nsf_df = format_nsf_data()

    # usda
    usda_df = format_usda_data()

    grants_df = grants_gov_df
    grants_df = grants_df[~grants_df['grant_title'].isnull()]
    # put grants gov first so it drops nsf duplicates
    grants_df = grants_df.append(nsf_df).drop_duplicates(['grant_title', 'grant_info_url'])
                            #.append(usda_df)\
                            #    .drop_duplicates(['grant_title', 'grant_info_url'])

    rows = []
    for row in grants_df.iterrows():
        rows.append(row[1].values.tolist())

    cur.executemany(insert_on_duplicate_update_sql, rows)


    # old code before ON DUPLICATE KEY UPDATE
    # sql = """INSERT INTO grants VALUES (""" + (" %s," * (len(grants_db_column_names) - 1)) + """ %s )"""
    # cur.executemany(sql, rows)

def init_faculty_previous_grants(cur):
    """ Initialize faculty previous grants from research_grant_history """
    punc_trans = str.maketrans(string.punctuation, " " * len(string.punctuation))
    num_trans = str.maketrans('', '', '1234567890')
    sw = set(stopwords.words('english'))
    wnl = wordnet.WordNetLemmatizer()
    faculty_grants = []

    grant_history_df = pd.read_csv('temp_data/research_grant_history.csv', delimiter=",")
    for index, row in grant_history_df.iterrows():
        uncleaned_name = row['PI Name']
        name = uncleaned_name.lower().translate(punc_trans)
        if "," in uncleaned_name:
            name = ' '.join(list(filter(lambda x: len(x) > 1, name.split(" ")))[::-1])
        # Removes stopwords and lemmatizes words. Remove if want to keep whole description
        title = row['Title']
        try:
            title = title.lower()
            title = title.translate(punc_trans)
            title = title.translate(num_trans)
            title = filter(lambda x: x.lower() not in sw, title.split())
            title = [wnl.lemmatize(x) for x in title]
            title = ' '.join(title)
            faculty_grants.append((title, name))
        except:
            continue

    new_grant_history_df = pd.read_csv('temp_data/bids_data.csv')
    for index, row in new_grant_history_df.iterrows():
        uncleaned_name = row['Investigator']
        name = uncleaned_name.lower().translate(punc_trans)
        if "," in uncleaned_name:
            name = ' '.join(list(filter(lambda x: len(x) > 1, name.split(" ")))[::-1])
        # Removes stopwords and lemmatizes words. Remove if want to keep whole description
        title = row['Title']
        try:
            title = title.lower()
            title = title.translate(punc_trans)
            title = title.translate(num_trans)
            title = filter(lambda x: x.lower() not in sw, title.split())
            title = [wnl.lemmatize(x) for x in title]
            title = ' '.join(title)
            faculty_grants.append((title, name))
        except:
            continue

    faculty_grants_stmt = "INSERT INTO faculty_grants (title, faculty) VALUES (%s, %s)"
    faculty_grants_rows = faculty_grants

    cur.executemany(faculty_grants_stmt, faculty_grants_rows)

def create_vectorizers():
    """ Create faculty_vectorizer and grant_vectorizer """
    sw = set(stopwords.words('english'))
    wnl = wordnet.WordNetLemmatizer()
    punc_trans = str.maketrans(string.punctuation, " " * len(string.punctuation))
    num_trans = str.maketrans('', '', '123456789')

    """ Preprocessing faculty data
        Computes TF-IDF over entire faculty corpus """
    faculty_df = pd.read_csv('temp_data/complete_cleaned_faculty_webpages.csv', delimiter=",")
    faculty_df = faculty_df[pd.notnull(faculty_df['cleaned_str_text'])]
    faculty_df.reset_index(drop=True)
    descriptions = faculty_df['cleaned_str_text']
    cleaned = []
    for desc in descriptions:
        try:
            desc = desc.lower()
            desc = desc.translate(punc_trans)
            desc = desc.translate(num_trans)
            first = filter(lambda x: x not in sw, desc.split())
            second = [wnl.lemmatize(x) for x in first]
            cleaned.append(second)
        except:
            continue

    faculty_corpus = [' '.join(doc) for doc in cleaned]
    faculty_vectorizer = TfidfVectorizer()
    faculty_matrix = faculty_vectorizer.fit_transform(faculty_corpus)

    with open('temp_data/faculty_vectorizer.pkl', 'wb') as output:
        pickle.dump(faculty_vectorizer, output, -1)

    """ Preprocessing grants data """
    grants_df = pd.read_csv('temp_data/grants_gov.csv', delimiter="~")
    descriptions = grants_df['Description']
    cleaned = []
    for desc in descriptions:
        try:
            desc = desc.lower()
            desc = desc.translate(punc_trans)
            desc = desc.translate(num_trans)
            first = filter(lambda word: word not in sw, desc.split())
            second = [wnl.lemmatize(word) for word in first]
            cleaned.append(second)
        except:
            continue

    grants_gov_corpus = [' '.join(doc) for doc in cleaned]

    """ Preprocessing prev faculty grants data """
    grant_history_df = pd.read_csv('temp_data/research_grant_history.csv', delimiter=",")
    descriptions = grant_history_df['Title']
    cleaned = []
    for desc in descriptions:
        try:
            desc = desc.lower()
            desc = desc.translate(punc_trans)
            desc = desc.translate(num_trans)
            first = filter(lambda word: word not in sw, desc.split())
            second = [wnl.lemmatize(word) for word in first]
            cleaned.append(second)
        except:
            continue
    grant_history_corpus = [' '.join(doc) for doc in cleaned]

    """ Preprocessing new prev faculty grants data """
    new_grant_history_df = pd.read_csv('temp_data/bids_data.csv', delimiter=",")
    descriptions = new_grant_history_df['Title']
    cleaned = []
    for desc in descriptions:
        try:
            desc = desc.lower()
            desc = desc.translate(punc_trans)
            desc = desc.translate(num_trans)
            first = filter(lambda word: word not in sw, desc.split())
            second = [wnl.lemmatize(word) for word in first]
            cleaned.append(second)
        except:
            continue
    new_grant_history_corpus = [' '.join(doc) for doc in cleaned]

    """ Preprocessing nsf grants data """
    nsf_df = pd.read_csv('temp_data/nsf.csv', delimiter="~")
    descriptions = nsf_df['Description']
    cleaned = []
    for desc in descriptions:
        try:
            desc = desc.lower()
            desc = desc.translate(punc_trans)
            desc = desc.translate(num_trans)
            first = filter(lambda word: word not in sw, desc.split())
            second = [wnl.lemmatize(word) for word in first]
            cleaned.append(second)
        except:
            continue
    nsf_corpus = [' '.join(doc) for doc in cleaned]
    
    # grants_corpus = grants_gov_corpus
    grants_corpus = grants_gov_corpus + grant_history_corpus + new_grant_history_corpus + nsf_corpus
    grants_vectorizer = TfidfVectorizer(max_df=30000)
    grants_vectorizer.fit(grants_corpus)

    with open('temp_data/grants_vectorizer.pkl', 'wb') as output:
        pickle.dump(grants_vectorizer, output, -1)



######################
## Helper Functions ##
######################

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

init_db()
