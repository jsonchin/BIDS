from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

app = Flask(__name__) # create the application instance :)

from .views import *
from .HTTP_requests import *

app.run()
