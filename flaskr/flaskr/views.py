from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

from flaskr.flaskr import app

from .data_management.database import *

from .utility import *

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

def get_faculty_vectorizer():
    with open('database_management/faculty_vectorizer.pkl', 'rb') as input:
        return pickle.load(input)

def get_grants_vectorizer():
    print("DF")
    with open('database_management/grants_vectorizer.pkl', 'rb') as input:
        return pickle.load(input)
