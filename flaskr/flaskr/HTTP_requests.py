from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

from flaskr import app

from .database import *

from .utility import *


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