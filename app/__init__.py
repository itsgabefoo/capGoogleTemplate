# Every level/folder of a Python application has an __init__.py file. The purpose of this file is to connect the levels
# of the app to each other. 

from mongoengine import *
from flask import Flask
import os
from flask_moment import Moment

app = Flask(__name__)

# this will geberate a random number each tiome this app is run to be the secret key because
# os.environ.get("SECRET_KEY") will fail because we do not have that variable set in the os.environment
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY") # or os.urandom(20)
# you must change the next line to be link to your database at mlab
connect("bullcoin", host='mongodb+srv://admin:bulldogz@cluster0.8m0v1.gcp.mongodb.net/bullcoin?retryWrites=true&w=majority')

moment = Moment(app)

from .routes import *
