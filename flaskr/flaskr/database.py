import MySQLdb

from flaskr import app

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




def get_table_columns(table_name):
    cur = db.cursor()

    cur.execute("""
        SELECT COLUMN_NAME FROM (
         SELECT * FROM INFORMATION_SCHEMA.COLUMNS
            WHERE table_name='faculty_vcr'
         ) T;""")  # SANITIZE PLEASE!
    return [c[0] for c in cur.fetchall()]


# @app.route('/')
#no need to route if you're just going to call it internally from a python fn
def get_faculty_vcr(faculty_name):
    cur = db.cursor()
    cur.execute('''SELECT * FROM faculty_vcr WHERE faculty_name=%s;''', (faculty_name,)) #SANITIZE PLEASE!
    rows = cur.fetchall()

    cur.close()
    return QueryResponse(rows, get_table_columns('faculty_vcr'))

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
    cur.close()
    return rows

def get_faculty_all_specific(faculty_name):
    cur = db.cursor()
    cur.execute('''
        SELECT * FROM faculty_vcr AS f1
            INNER JOIN faculty_webpages AS f2
                ON f1.faculty_name = f2.faculty_name
            WHERE f1.faculty_name=%s;''', (faculty_name, ))
    rows = cur.fetchall()
    cur.close()
    return rows


def insert_grant(grant_d):
    cur = db.cursor()

    grant_cols = []

    sql = '''INSERT INTO grants VALUES ( ''' + ("%s, "*(len(grant_cols) - 1)) + "%s )"

    cur.execute(sql, [grant_d[col] for col in grant_cols])  # SANITIZE PLEASE!
    cur.close()

    db.commit()

def remove_grant(grant_d):
    cur = db.cursor()

    sql = '''DELETE FROM grants WHERE grant_name=%s'''

    cur.execute(sql, [grant_d['grant_name']])
    cur.close()

    db.commit()

def get_all_grants():
    cur = db.cursor()
    cur.execute('''SELECT * FROM grants;''')
    rows = cur.fetchall()
    cur.close()
    return rows