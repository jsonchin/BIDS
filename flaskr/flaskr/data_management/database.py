import MySQLdb
from flask import g
# from .database_utilities import *
# from .database_info import *
import datetime
import pytz


"""
faculty_vcr
    -vcresearch profile information

faculty_webpages
    -personal webpages bag of words

grants
    -grants from different sources
        -grants.gov
        -nsf

grants_user_input
    -user/manually inputted grants

faculty_grants
    -faculty_name-grant_name pairs
"""


# ALL functions in this file return a QueryResponse if they return anything
# if not returning anything (updating/inserting/removing records), then should db.commit() to save changes
# QueryResponse.rows is of the format (('a', 'b', 'c'), ('d', 'e', 'f'), ..., ('x', 'y', 'z'))
# even for single column queries (('a'), ('b'), ('c'))
class QueryResponse():
     def __init__(self, rows, column_names):
         self.rows = rows
         self.column_names =  column_names

def connect_db():
    db = MySQLdb.connect(
        host='127.0.0.1',
        user='root',
        passwd='pw',
        db='brdo'
    )
    return db

def get_db():
    try:
        if not hasattr(g, 'mysqldb'):
            g.mysqldb = connect_db()
        return g.mysqldb
    except:
        return connect_db()


# @app.route('/')
#no need to route if you're just going to call it internally from a python fn
def get_faculty_vcr(faculty_name):
    db = get_db()
    cur = db.cursor()
    cur.execute('''SELECT * FROM faculty_vcr WHERE faculty_name=%s;''', (faculty_name,)) #SANITIZE PLEASE!
    rows = cur.fetchall()
    return QueryResponse(rows, [l[0] for l in cur.description])

def get_faculty_grants():
    db = get_db()
    cur = db.cursor()
    cur.execute('''SELECT * FROM faculty_grants;''')
    rows = cur.fetchall()
    return QueryResponse(rows, [l[0] for l in cur.description])

def get_faculty_names():
    db = get_db()
    cur = db.cursor()
    cur.execute('''SELECT faculty_name FROM faculty_vcr;''')
    rows = cur.fetchall()
    return QueryResponse(rows, [l[0] for l in cur.description])
    # cur.close()
    # return [t[0] for t in rows]

def get_faculty_webpages():
    db = get_db()
    cur = db.cursor()
    cur.execute('''
        SELECT * FROM faculty_webpages;''')
    rows = cur.fetchall()
    return QueryResponse(rows, [l[0] for l in cur.description])


def get_faculty_all():
    db = get_db()
    cur = db.cursor()
    cur.execute('''
        SELECT * FROM faculty_vcr AS f1
            INNER JOIN faculty_webpages AS f2
                ON f1.faculty_name = f2.faculty_name;''')
    rows = cur.fetchall()
    return QueryResponse(rows, [l[0] for l in cur.description])

def get_faculty_all_specific(faculty_name):
    db = get_db()
    cur = db.cursor()
    cur.execute('''
        SELECT * FROM faculty_vcr AS f1
            INNER JOIN faculty_webpages AS f2
                ON f1.faculty_name = f2.faculty_name
            WHERE f1.faculty_name=%s;''', (faculty_name, ))
    rows = cur.fetchall()
    return QueryResponse(rows, [l[0] for l in cur.description])


def insert_grant(grant_d):
    db = get_db()
    cur = db.cursor()

    sql = '''INSERT INTO grants_user_input VALUES ( ''' + ("%s, "*(len(grants_db_column_names) - 1)) + "%s )"

    grant_d[grants_db_column_names[-1]] = get_current_time() #grant_db_insert_date

    cur.execute(sql, [grant_d[col] for col in grants_db_column_names])  # SANITIZE PLEASE!
    cur.close()

    db.commit()

def remove_grant(grant_d):
    """
    Deletes grant if exists from both the source grant table and the user input grant table
    :param grant_d:
    :return:
    """
    db = get_db()
    cur = db.cursor()

    sql = '''DELETE FROM grants WHERE grant_title=%s AND grants_gov_url=%s'''
    cur.execute(sql, [grant_d['grant_name'], grant_d['grants_gov_url']])

    sql = '''DELETE FROM grants_user_input WHERE grant_title=%s AND grants_gov_url=%s'''
    cur.execute(sql, [grant_d['grant_name'], grant_d['grants_gov_url']])

    cur.close()

    db.commit()

def get_all_grants():
    db = get_db()
    cur = db.cursor()
    cur.execute('''SELECT * FROM grants;''')
    rows = cur.fetchall()
    cur.close()
    return QueryResponse(rows, [l[0] for l in cur.description])

# def get_top_k_recent_grants(k=10, offset=0):
#     cur = db.cursor()
#     cur.execute('''SELECT * FROM grants ORDER BY grant_db_insert_date;''')
#     rows = cur.fetchall()
#     cur.close()
#     return QueryResponse(rows, [l[0] for l in cur.description])

def get_offset_k_recent_grants(k=10, offset=0):
    db = get_db()
    cur = db.cursor()
    cur.execute('''SELECT * FROM grants ORDER BY grant_db_insert_date LIMIT %s OFFSET %s;''', [k, offset])
    rows = cur.fetchall()
    cur.close()
    return QueryResponse(rows, [l[0] for l in cur.description])


def remove_outdated_grants():
    """
    Removes all grants from both grants and grants_user_input that have a deadline less than today
    :return:
    """
    db = get_db()
    cur = db.cursor()
    today_date = get_current_date()
    sql = """DELETE FROM grants WHERE grant_closing_date < %s;"""
    cur.execute(sql, [today_date])
    sql = """DELETE FROM grants_user_input WHERE grant_closing_date < %s;"""
    cur.execute(sql, [today_date])
    cur.close()
    # return QueryResponse(rows, [l[0] for l in cur.description])
    db.commit()


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

def get_current_time():
    return str(datetime.datetime.now(pytz.timezone('US/Pacific')))[:19]

def get_current_date():
    return str(datetime.datetime.now(pytz.timezone('US/Pacific')))[:10]