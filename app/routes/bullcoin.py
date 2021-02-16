# This file contains all the routes for the Feedback functionality

from app import app
from flask import render_template, redirect, url_for, session, flash
from app.classes.data import User, Bullcoin, Transaction, Service
#from app.classes.forms import 
import datetime as dt
from bson.objectid import ObjectId

@app.route('/admin')
def admin():
    currUser = User.objects.get(pk = session['currUserId'])
    if currUser.admin:
        numBankCoins = Bullcoin.objects(owner=None).count()
        allCoinOwners = User.objects(coins__exists = True)
        print(allCoinOwners)
        return render_template("admin.html", numBankCoins=numBankCoins, coinOwners=allCoinOwners)
    else:
        flash(f"You are not an admin.")
        return redirect('profile')

@app.route('/coinmint/<amt>')
def coinmint(amt):
    currUser = User.objects.get(pk = session['currUserId'])
    if currUser.admin:
        amt = int(amt)
        numBankCoins = Bullcoin.objects(owner=None).count()
        if amt > 0:
            for n in range(amt):
                Bullcoin().save()
            flash(f"{abs(amt)} Bullcoins Created.")
        elif amt < 0:
            if numBankCoins >= abs(amt):
                delBullcoins = Bullcoin.objects(owner=None).limit(abs(amt))
                delBullcoins.delete()
                flash(f"{abs(amt)} Bullcoins Deleted.")
            else:
                flash(f"The Bank has {numBankCoins} coins but you tried to delete {abs(amt)}.")
    
    return redirect(url_for('admin'))

@app.route('/bankcoingive/<useremail>/<amt>')
def coingive(useremail,amt):
    currUser = User.objects.get(pk=session['currUserId'])
    if currUser.admin:
        amt = int(amt)
        numBankCoins = Bullcoin.objects(owner=None).count()
        getter = User.objects.get(email=useremail)
        if amt > numBankCoins:
            flash(f"The bank has {numBankCoins} coins but you asked for {amt}.")

        # Give coins from the bank to the user
        elif amt > 0:
            giveBankCoins = Bullcoin.objects(owner=None).limit(amt)
            for coin in giveBankCoins:
                coin.update(
                    owner = getter
                )
                getter.coins.append(coin)
            getter.save()

        # remove coins from the user and give them to the bank
        elif amt < 0:

            # Get the ammount of coins the getter has
            numGetterCoins = Bullcoin.objects(owner=getter).count()

            # if they don't have enough coins...
            if numGetterCoins < abs(amt):
                flash(f"Getter has {numGetterCoins} and you tried to take {abs(amt)} coins.")
                return redirect(url_for('admin'))

            # Get all of the getter's coins that are going to be given back to the bank
            getterCoins = Bullcoin.objects(owner=getter)

            # Remove the getter from the coins owner field
            for coin in getterCoins:
                coin.update(
                    owner = None
                )

            # Remove all the coins from the user's list too
            getter.update(
                pull_all__following = getterCoins
                )

            flash(f"{abs(amt)} coins were taken from {getter.gfname} {getter.glname} and given back to the bank.")
        return redirect(url_for("admin"))