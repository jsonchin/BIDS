from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

from flaskr import app


def render_page(html_file_name, css_file):
    return render_template('page_template.html',
                           main_content=render_template(html_file_name),
                           css_file=url_for('static', filename=css_file))

@app.route('/')
def show_index():
    return render_page('index.html', 'index.css')

@app.route('/manual_grant')
def show_manual_grant():
    return render_page('manual_grant.html', 'manual_grant.css')

@app.route('/grant_search')
def show_grant_search():
    return render_page('grant_search.html', 'manual_grant.css')

@app.route('/faculty_search')
def show_faculty_search():
    return render_page('faculty_search.html', 'manual_grant.css')