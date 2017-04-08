from flask import request, url_for, render_template

from flaskr.flaskr import app
from flaskr.flaskr.data_management.database import *
from .utility import *
from .matching import *


def render_page(html_file_name, css_file):
    return render_template('page_template.html',
                           main_content=render_template(html_file_name),
                           css_file=url_for('static', filename='css/{}'.format(css_file)))

@app.route('/faculty_search_query', methods=['POST'])
def get_faculty_query_html():
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

    grant_matches_html = get_top_k_grants_html(d['description'])

    return render_template('response/faculty_query_response.html', grant_matches_html=grant_matches_html,
                                        faculty_img=img_path,
                                        **d) #unpack the dictionary as keyword arguments

@app.route('/manual_grant_submit', methods=['POST'])
def post_manual_grant_html():
    #insert into db
    print( list(request.form.keys()) )
    print(request.form['inputGrantTitle'])
    print(request.form['inputDescription'])
    print(request.form['inputGrantDeadline'])
    print(request.form['inputGrantAmt'])
    print(request.form['inputURLAdditionalInfo'])
    return ''

@app.route('/manual_faculty_submit', methods=['POST'])
def post_manual_faculty_submit_html():
    """
    faculty_name,
    faculty_department
    faculty_description
    Lots of blank fields/optional fields
    :return:
    """
    return ''

@app.route('/grant_get_top_k_faculty', methods=['POST'])
def get_top_k_faculty_for_grant_html():
    #get grant data
    #get faculty
    #want faculty names to lookup in database
    #or alternatively all of the info the faculty
    #render cards for faculty, or pass in data of faculty, list of dictionaries to render in grant_top_k_faculty.html

    grant_description = request.form['grant_description']
    grant_title = request.form['grant_title']

    faculty_matches = get_k_closest_faculty(grant_description)

    for faculty_d in faculty_matches:
        faculty_d['faculty_img_url'] = url_for('static', filename='images/faculty_images/{}'.format(faculty_d['faculty_name']))
        faculty_d['faculty_name'] = captialize_name(faculty_d['faculty_name'])

    return render_template('response/top_k_similar_faculty.html', faculty_matches=faculty_matches)



def get_top_k_grants_html(corpus):
    grant_matches = get_k_closest_grants(corpus)

    return render_template('response/top_k_similar_grants.html', grants=grant_matches)



@app.route('/faculty_get_top_k_grants', methods=['POST'])
def get_top_k_grants_for_faculty_html():
    #get grant data
    #get faculty
    #want faculty names to lookup in database
    #or alternatively all of the info the faculty
    #render cards for faculty, or pass in data of faculty, list of dictionaries to render in grant_top_k_faculty.html

    faculty_description = request.form['faculty_description']

    return get_top_k_grants_html(faculty_description)


@app.route('/get_k_more_grants', methods=['POST'])
def get_k_more_grants_html():
    try:
        offset = int(request.form['offset'])
    except:
        offset = 0
    try:
        k = int(request.form['k'])
    except:
        k = 10
    qr = get_offset_k_recent_grants(k=k, offset=offset)
    grants = qr.rows
    column_names = qr.column_names
    return render_template('response/k_grants.html', grants=grants)