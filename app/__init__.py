# Every level/folder of a Python application has an __init__.py file. The purpose of this file is to connect the levels
# of the app to each other. 

from mongoengine import *
from flask import Flask
import os
from flask_moment import Moment


app = Flask(__name__)

# this will geberate a random number each tiome this app is run to be the secret key because
# os.environ.get("SECRET_KEY") will fail because we do not have that variable set in the os.environment
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY") or os.urandom(20)
# you must change the next line to be link to your database at mlab

from app.credentials import mongo_user, mongo_pw

#connect("capGoogleTemplate", host='mongodb+srv://capGoogleTemplate:bu11dogz@cluster0.8m0v1.mongodb.net/capGoogleTemplate?retryWrites=true&w=majority')
connect("capGoogleTemplate", host=f'mongodb+srv://{mongo_user}:{mongo_pw}@cluster0.8m0v1.mongodb.net/capGoogleTemplate?retryWrites=true&w=majority')

moment = Moment(app)

from .routes import *


