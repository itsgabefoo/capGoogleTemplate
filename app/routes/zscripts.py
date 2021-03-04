from app import app
from flask import render_template, redirect, url_for
# This imports the data classes your created in the data file in the classes folder
from app.classes.data import User, Bullcoin, Approval
# This imports all the needed forms classes from the forms file in the classes folder

@app.route('/resetbullcoin')
def resetbullcoin():
    users = User.objects()
    users.update(
        unset__gavecoins = 1,
        unset__gotcoins = 1
    )
    pass