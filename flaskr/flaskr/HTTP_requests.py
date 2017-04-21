from flask import request, url_for, render_template

from .flaskr import app
from .utility import *
from .matching import *
from .matching_tfidf import *

import os


#########################
## HTTP Request Routes ##
#########################

@app.route('/faculty_search_query', methods=['POST'])
def get_faculty_query_html():
    """
    Given a faculty_name in a POST request, returns html that contains their faculty card and top k grant matches
    :return: html
    """
    faculty_name = request.form['faculty_name'].lower()
    qr = get_faculty_vcr(faculty_name)
    column_names = qr.column_names
    row = qr.rows[0]

    faculty_d = {}
    for i in range(len(column_names)):
        if i >= len(row):
            faculty_d[column_names[i]] = ''
        else:
            faculty_d[column_names[i]] = row[i]

    faculty_d['faculty_img_url'] = get_faculty_profile_img(faculty_d['faculty_name'])
    faculty_d['faculty_name'] = captialize_name(faculty_d['faculty_name'])

    grant_matches_html = get_top_k_grants_html(faculty_d['description'],
                                               show_faculty_matches=False)

    faculty_card_html = render_template('response/k_faculty.html',
                                        faculty_l=[faculty_d], is_faculty_matching=False)

    return render_template('response/faculty_query_response.html',
                           grant_matches_html=grant_matches_html,
                           faculty_card_html=faculty_card_html)


@app.route('/grant_get_top_k_faculty', methods=['POST'])
def get_top_k_faculty_for_grant_html():
    """
    Given a grant_description in a POST request, returns html that shows the top k matches for this grant
    :return: html
    """
    grant_description = request.form['grant_description']
    # grant_title = request.form['grant_title']

    return get_top_k_faculty_html(grant_description)

@app.route('/faculty_get_top_k_grants', methods=['POST'])
def get_top_k_grants_for_faculty_html():
    """
    Given a corpus in a POST request, returns html that shows the top k matches for this faculty member
    :return: html
    """
    corpus = request.form['corpus']
    return get_top_k_grants_html(corpus, show_faculty_matches=False)

@app.route('/get_k_more_grants', methods=['POST'])
def get_k_more_grants_html():
    """
    Given an offset and k in a POST request, returns html that shows the next k grants
    :return: html
    """
    offset = int(request.form.get('offset', 0))
    k = int(request.form.get('k', 10))
    qr = get_offset_k_recent_grants(k=k, offset=offset)
    grants_l = qr.rows
    column_names = qr.column_names
    grants = []
    for row in grants_l:
        grants.append({col:row_val for col, row_val in zip(column_names, row)})

    return render_template('response/k_grants.html', grants=grants, show_faculty_matches=True)



######################
## Helper Functions ##
######################


def get_faculty_profile_img(faculty_name):
    """
    Gets the faculty_profile_img path for a faculty_name if it exists, otherwise output default_img path
    :param faculty_name: str
    :return: str path to img
    """
    img_path = url_for('static', filename='images/faculty_images/{}'.format(faculty_name))
    if not os.path.isfile(img_path[1:].replace('%20', ' ')):
        return url_for('static', filename='images/faculty_images/default_img')
    return img_path

def get_top_k_faculty_html(corpus, k=5, is_faculty_matching=True):
    # faculty_matches = get_k_closest_faculty(corpus, k=k)
    faculty_matches = get_top_k_faculty_tfidf(corpus, k=k) #jerry's tfidf

    for faculty_d in faculty_matches:
        faculty_d['faculty_img_url'] = get_faculty_profile_img(faculty_d['faculty_name'])
        faculty_d['faculty_name'] = captialize_name(faculty_d['faculty_name'])

    return render_template('response/k_faculty.html', faculty_l=faculty_matches, is_faculty_matching=is_faculty_matching)

def get_top_k_grants_html(corpus, k=10, show_faculty_matches=True):
    grant_matches = get_k_closest_grants(corpus, k)
    return render_template('response/k_grants.html', grants=grant_matches, show_faculty_matches=show_faculty_matches)






###################
## Unimplemented ##
###################

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