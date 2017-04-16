from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

from .flaskr import app

from .data_management.database import *

from .utility import *

from .HTTP_requests import get_k_more_grants_html

# Add tabs to the sidebar here (name, route)
TABS = [
        ('Index', '/'),
        ('Individual Grant Matching', '/manual_grant'),
        ('Individual Faculty Matching', '/manual_faculty'),
        ('Grant Search', '/grant_search'),
        ('Faculty Search', '/faculty_search')
    ]

###########
## Views ##
###########

@app.route('/')
def show_index():
    return render_page('index.html', [], [])

@app.route('/manual_grant')
def show_manual_grant():
    return render_page('manual_grant.html',
                       ['manual_grant.css', 'faculty_card.css'],
                       ['manual_grant.js', 'card.js'])

@app.route('/manual_faculty')
def show_manual_faculty():
    return render_page('manual_faculty.html',
                       ['manual_faculty.css', 'grant_card.css'],
                       ['manual_faculty.js', 'card.js'])

@app.route('/grant_search')
def show_grant_search():
    k_grants_html = get_k_more_grants_html()

    grant_search_html = render_template('grant_search.html', k_grants_html=k_grants_html)

    return render_page_with_html(grant_search_html,
                                 ['grant_search.css', 'faculty_card.css', 'grant_card.css'],
                                 ['grant_search.js', 'card.js'])

@app.route('/faculty_search')
def show_faculty_search():
    qr = get_faculty_names()

    faculty_names = [captialize_name(row[0]) for row in qr.rows]

    faculty_search_html = render_template('faculty_search.html', faculty_names=faculty_names)

    return render_page_with_html(faculty_search_html,
                                 ['faculty_search.css', 'faculty_card.css', 'grant_card.css'],
                                 ['faculty_search.js', 'card.js'])


######################
## Helper Functions ##
######################

# All pages built with page_template.html and page.css as the base template

def render_page(html_file_name, css_files, js_files):
    return render_page_with_html(render_template(html_file_name), css_files, js_files)

def render_page_with_html(html, css_files, js_files):
    # Initialize tabs for the sidebar
    tabs_d = []
    for tab in TABS:
        tabs_d.append({'name':tab[0], 'route':tab[1]})

    return render_template('page_template.html',
                           tabs_d=tabs_d,
                           main_content=html,
                           css_files=[url_for('static', filename='css/{}'.format(file_name)) for file_name in css_files],
                           js_files=[url_for('static', filename='js/{}'.format(file_name)) for file_name in js_files])