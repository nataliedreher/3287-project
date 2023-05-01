import sqlite3

from flask import Flask, redirect, g, url_for, request, render_template, make_response, session, flash

app = Flask(__name__)

class PrefixMiddleware(object):
    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        # set the prefix for all url to the Jupyterhub URL for my virtual machine
        # this path is set to my user [KNOX] and port [3308] 
        # (see the code at bottom to see how port is set to 3308 instead of 5000)
        environ['SCRIPT_NAME'] = "/" 
       
        # call the default processing
        return self.app(environ, start_response)

# insert our proxy setting url class as wrapper to the app
app.wsgi_app = PrefixMiddleware(app.wsgi_app)


def get_db_connection():
    conn = sqlite3.connect('database.db')
    return conn

@app.route('/')
def index():
    return make_response(render_template("index.html"))