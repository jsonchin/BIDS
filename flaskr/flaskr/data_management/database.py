import MySQLdb

# from flaskr.flaskr.data_management.format_grant_data_sources import format_grants_gov_data
import flaskr.flaskr.data_management.database_utilities as db_utils
import flaskr.flaskr.data_management.database_info as db_info


db =MySQLdb.connect(
    host='localhost',
    user='root',
    passwd='pw',
    db='brdo'
)

class QueryResponse():
     def __init__(self, rows, column_names):
         self.rows = rows
         self.column_names =  column_names



# Use cur.description to get column names
# def get_table_columns(table_name):
#     cur = db.cursor()
#
#     cur.execute("""
#         SELECT COLUMN_NAME FROM (
#          SELECT * FROM INFORMATION_SCHEMA.COLUMNS
#             WHERE table_name='faculty_vcr'
#          ) T;""")  # SANITIZE PLEASE!
#     return [c[0] for c in cur.fetchall()]


# @app.route('/')
#no need to route if you're just going to call it internally from a python fn
def get_faculty_vcr(faculty_name):
    cur = db.cursor()
    cur.execute('''SELECT * FROM faculty_vcr WHERE faculty_name=%s;''', (faculty_name,)) #SANITIZE PLEASE!
    rows = cur.fetchall()

    return QueryResponse(rows, [l[0] for l in cur.description])

def get_faculty_names():
    cur = db.cursor()
    cur.execute('''SELECT faculty_name FROM faculty_vcr;''')
    rows = cur.fetchall()
    cur.close()
    return [t[0] for t in rows]


def get_faculty_all():
    cur = db.cursor()
    cur.execute('''
        SELECT * FROM faculty_vcr AS f1
            INNER JOIN faculty_webpages AS f2
                ON f1.faculty_name = f2.faculty_name;''')
    rows = cur.fetchall()
    return QueryResponse(rows, [l[0] for l in cur.description])

def get_faculty_all_specific(faculty_name):
    cur = db.cursor()
    cur.execute('''
        SELECT * FROM faculty_vcr AS f1
            INNER JOIN faculty_webpages AS f2
                ON f1.faculty_name = f2.faculty_name
            WHERE f1.faculty_name=%s;''', (faculty_name, ))
    rows = cur.fetchall()
    return QueryResponse(rows, [l[0] for l in cur.description])


def insert_grant(grant_d):
    cur = db.cursor()

    sql = '''INSERT INTO grants_user_input VALUES ( ''' + ("%s, "*(len(db_info.grants_db_column_names) - 1)) + "%s )"

    grant_d[db_info.grants_db_column_names[-1]] = db_utils.get_current_time() #grant_db_insert_date

    cur.execute(sql, [grant_d[col] for col in db_info.grants_db_column_names])  # SANITIZE PLEASE!
    cur.close()

    db.commit()

def remove_grant(grant_d):
    """
    Deletes grant if exists from both the source grant table and the user input grant table
    :param grant_d:
    :return:
    """
    cur = db.cursor()

    sql = '''DELETE FROM grants WHERE grant_title=%s AND grants_gov_url=%s'''
    cur.execute(sql, [grant_d['grant_name'], grant_d['grants_gov_url']])

    sql = '''DELETE FROM grants_user_input WHERE grant_title=%s AND grants_gov_url=%s'''
    cur.execute(sql, [grant_d['grant_name'], grant_d['grants_gov_url']])

    cur.close()

    db.commit()

def get_all_grants():
    cur = db.cursor()
    cur.execute('''SELECT * FROM grants;''')
    rows = cur.fetchall()
    cur.close()
    return rows


def TEMP_get_k_grants(k=10):
    cur = db.cursor()
    cur.execute('''SELECT * FROM grants LIMIT %s;''', [k])
    rows = cur.fetchall()
    cur.close()
    return QueryResponse(rows, [l[0] for l in cur.description])