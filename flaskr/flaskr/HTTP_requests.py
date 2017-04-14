import nltk.stem.wordnet as wordnet
import numpy as np
import string

from flask import request, url_for, render_template
from flaskr.flaskr import app
from flaskr.flaskr.data_management.database import *
from nltk.corpus import stopwords
from .utility import *

sw = set(stopwords.words('english'))
wnl = wordnet.WordNetLemmatizer()
punc_trans = str.maketrans(string.punctuation, " " * len(string.punctuation))
num_trans = str.maketrans('', '', '123456789')

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
    print(1)
    faculty_grants = get_faculty_grants().rows
    print(2)
    grants_vectorizer = get_grants_vectorizer()
    print(3)
    
    # Need to store into db

    grant_title = request.form['inputGrantTitle']
    grant_description = request.form['inputDescription']
    grant_deadline = request.form['inputGrantDeadline']
    grant_amount = request.form['inputGrantAmt']
    grant_info = request.form['inputURLAdditionalInfo']

    desc = grant_description
    try:
        desc = desc.lower()
        desc = desc.translate(punc_trans)
        desc = desc.translate(num_trans)
        first = filter(lambda x: x not in sw, desc.split())
        cleaned = [wnl.lemmatize(x) for x in first]
    except:
        cleaned = ["Nothing"]

    cleaned = [' '.join(cleaned)]
    print(cleaned)

    new_grant = grants_vectorizer.transform(cleaned).T

    closest_grants = []
    for title, faculty in faculty_grants:
        old_grant = grants_vectorizer.transform([title])
        # Uses dot similarity
        closest_grants.append((np.dot(old_grant, new_grant).toarray()[0][0], faculty))
        # closest_grants.append((np.dot(training_grant, test_grant.T), index)) <--- For SVD
        
    # Finds the 10 grants that are closest to the test grant
    max_product = max(closest_grants)[0]
    faculty_and_score = [(x[0] / max_product, x[1]) for x in sorted(closest_grants)[-5:]]
    print(faculty_and_score)
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

def get_faculty_vectorizer():
    with open('data_management/faculty_vectorizer.pkl', 'rb') as input:
        return pickle.load(input)

def get_grants_vectorizer():
    with open('data_management/grants_vectorizer.pkl', 'rb') as input:
        return pickle.load(input)