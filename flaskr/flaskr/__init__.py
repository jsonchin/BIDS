import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash


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