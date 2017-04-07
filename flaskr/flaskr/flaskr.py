
#from .views import *
#from .HTTP_requests import *
#from .data_management.database import *

import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

from .utility import *



app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py

app.debug = True
app.config['DEBUG'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'brdo.db'),
    # SECRET_KEY='development key',
    USERNAME='root',
    PASSWORD='pw'
))

app.config.update(dict(
    MYSQL_DATABASE_USER='root',
    MYSQL_DATABASE_PASSWORD='pw',
    MYSQL_DATABASE_DB='brdo'
))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def render_page(html_file_name, css_file):
    return render_template('page_template.html',
                           main_content=render_template(html_file_name),
                           css_file=url_for('static', filename='css/{}'.format(css_file)))

@app.route('/faculty_search_query', methods=['POST'])
def get_faculty_query():
    faculty_name = request.form['faculty_name'].lower()
    qr = get_faculty_vcr(faculty_name)
    column_names = qr.column_names
    row = qr.rows[0]

    d = {}
    for i in range(len(column_names)):
        if i >= len(row):
            d[column_names[i]] = ''
        else:
            d[column_names[i]] = row[i]

    d['faculty_name'] = captialize_name(d['faculty_name'])

    img_path = url_for('static', filename='images/faculty_images/{}'.format(faculty_name))

    return render_template('response/faculty_query_response.html', faculty_img=img_path, **d) #unpack the dictionary as keyword arguments

@app.route('/manual_grant_submit', methods=['POST'])
def post_manual_grant():
    #insert into db
    print( list(request.form.keys()) )
    print(request.form['inputGrantTitle'])
    print(request.form['inputDescription'])
    print(request.form['inputGrantDeadline'])
    print(request.form['inputGrantAmt'])
    print(request.form['inputURLAdditionalInfo'])
    return ''

@app.route('/manual_faculty_submit', methods=['POST'])
def post_manual_faculty_submit():
    """
    faculty_name,
    faculty_department
    faculty_description
    Lots of blank fields/optional fields
    :return:
    """
    return ''

@app.route('/grant_get_top_k_faculty', methods=['POST'])
def get_top_k_faculty_for_grant():
    #get grant data
    #get faculty
    #want faculty names to lookup in database
    #or alternatively all of the info the faculty
    #render cards for faculty, or pass in data of faculty, list of dictionaries to render in grant_top_k_faculty.html
    return render_template('response/grant_top_k_faculty.html', faculty_matches=[1,1,1])

def render_page(html_file_name, file_name):

    tabs = [
        ('Index', '/'),
        ('Manual Grant Submission', '/manual_grant'),
        ('Grant Search', '/grant_search'),
        ('Faculty Search', '/faculty_search')
    ]
    tabs_d = []
    for tab in tabs:
        tabs_d.append({'name':tab[0], 'route':tab[1]})



    return render_template('page_template.html',
                           tabs_d=tabs_d,
                           main_content=render_template(html_file_name),
                           css_file=url_for('static', filename='css/{}.css'.format(file_name)),
                           js_file=url_for('static', filename='js/{}.js'.format(file_name) ) )


def render_page_with_html(html, file_name):

    tabs = [
        ('Index', '/'),
        ('Manual Grant Submission', '/manual_grant'),
        ('Grant Search', '/grant_search'),
        ('Faculty Search', '/faculty_search')
    ]
    tabs_d = []
    for tab in tabs:
        tabs_d.append({'name':tab[0], 'route':tab[1]})



    return render_template('page_template.html',
                           tabs_d=tabs_d,
                           main_content=html,
                           css_file=url_for('static', filename='css/{}.css'.format(file_name)),
                           js_file=url_for('static', filename='js/{}.js'.format(file_name) ) )

@app.route('/')
def show_index():
    return render_page('index.html', 'index')

@app.route('/manual_grant')
def show_manual_grant():
    return render_page('manual_grant.html', 'manual_grant')

@app.route('/grant_search')
def show_grant_search():
    qr = TEMP_get_k_grants()
    grants = qr.rows
    column_names = qr.column_names
    # for grant in grants:
    #     grant[0] = grant[0].decode('utf8')

    faculty_search_html = render_template('grant_search.html', grants=grants, column_names=column_names)

    return render_page_with_html(faculty_search_html, 'manual_grant')

@app.route('/faculty_search')
def show_faculty_search():
    faculty_names = get_faculty_names()

    faculty_names = [captialize_name(name) for name in faculty_names]

    faculty_search_html = render_template('faculty_search.html', faculty_names=faculty_names)

    return render_page_with_html(faculty_search_html, 'faculty_search')
