from flask import request, url_for, render_template

from flaskr.flaskr import app
from flaskr.flaskr.data_management.database import *
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