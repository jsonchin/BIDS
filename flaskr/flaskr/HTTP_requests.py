from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

from flaskr import app


def render_page(html_file_name, css_file):
    return render_template('page_template.html',
                           main_content=render_template(html_file_name),
                           css_file=url_for('static', filename='css/{}'.format(css_file)))

@app.route('/faculty_query', methods=['GET'])
def get_faculty_query():
    faculty_name = request.form['faculty_name']
    return render_template('response/faculty_query_response.html', faculty_name=faculty_name)

@app.route('/manual_grant_submit', methods=['POST'])
def post_manual_grant():
    #insert into db
    return ''