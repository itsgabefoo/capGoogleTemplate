from app import app
from flask import render_template, redirect, url_for, session, flash
from app.classes.data import User, Bullcoin, Transaction, Service
from app.classes.forms import ServiceForm
import datetime as dt
from bson.objectid import ObjectId

@app.route('/admin')
def admin():
    currUser = User.objects.get(pk = session['currUserId'])
    if currUser.admin:
        numBankCoins = Bullcoin.objects(owner=None).count()
        numTotalCoins = Bullcoin.objects().count()

        # this is a mongodb aggregation that groups by the owner field and then counts the number of records in each grou[]
        pipeline=[
            { "$group" : { "_id": "$owner", "count" : { "$sum" : 1 } } }
            ]
        coinOwners = Bullcoin.objects().aggregate(pipeline)

        # need to get the User object from the ObjectId that is the result of the aggregation operation
        coinOwnersDisplay = []
        for coinOwner in coinOwners:
            if coinOwner['_id'] == None:
                coinOwner['_id'] = "Bank"
            else:
                coinOwner['_id'] = User.objects.get(pk=coinOwner['_id'])
            coinOwnersDisplay.append(coinOwner)

        return render_template("admin.html", numBankCoins=numBankCoins, numTotalCoins=numTotalCoins, coinOwners=coinOwnersDisplay)
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

# TODO make a version of this script to give x coins to all users
# might need to do do it with a jQuery round trip so that each user is a seperate request to avoid timeout
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

        # remove coins from the user and give them to the bank
        elif amt < 0:

            # Get the ammount of coins the getter has
            numGetterCoins = Bullcoin.objects(owner=getter).count()

            # if they don't have enough coins...
            if numGetterCoins < abs(amt):
                flash(f"Getter has {numGetterCoins} and you tried to take {abs(amt)} coins.")
                return redirect(url_for('admin'))

            # Get all of the getter's coins that are going to be given back to the bank
            getterCoins = Bullcoin.objects(owner=getter).limit(abs(amt))

            # Remove the getter from the coins owner field
            for coin in getterCoins:
                coin.update(
                    owner = None
                )

            flash(f"{abs(amt)} coins were taken from {getter.fname} {getter.lname} and given back to the bank.")
        return redirect(url_for("admin"))

@app.route('/service/<serviceid>')
def service(serviceid):
    service=Service.objects.get(pk=serviceid)
    return render_template('service.html', service=service)

@app.route('/services')
def services():
    services=Service.objects()
    return render_template('services.html',services=services)

@app.route('/servicenew', methods=['GET', 'POST'])
def servicenew():

    form = ServiceForm()

    if form.validate_on_submit():
        currUser=User.objects.get(pk=session['currUserId'])

        if form.type_.data=="Provider":
            newService = Service(
                provider=currUser
            )
        else:
            newService = Service(
                applicant=currUser
            )
        newService.owner=currUser
        newService.datetime=form.datetime.data
        newService.category=form.category.data
        newService.subject=form.subject.data
        newService.desc=form.desc.data
        newService.type_=form.type_.data
        newService.verified=False
        newService.save()

        return redirect(url_for('service',serviceid=newService.id))

    return render_template('serviceform.html',form=form, service=None)

@app.route('/serviceedit/<serviceid>', methods=['GET', 'POST'])
def serviceedit(serviceid):
    editService = Service.objects.get(pk=serviceid)
    if not session['admin'] and not str(session['currUserId']) == str(editService.owner.id):
        flash('You are are not the owner of this service.')
        return redirect(url_for('service',serviceid=editService.id))

    form = ServiceForm()
    if form.validate_on_submit():
        currUser=User.objects.get(pk=session['currUserId'])
        if form.type_.data=="Provider":
            editService.update(
                provider=currUser,
                datetime=form.datetime.data,
                category=form.category.data,
                subject=form.subject.data,
                desc=form.desc.data
            )
        else:
            editService.update(
                applicant=currUser,
                datetime=form.datetime.data,
                category=form.category.data,
                subject=form.subject.data,
                desc=form.desc.data
            )
        editService.reload()
        return redirect(url_for('service',serviceid=editService.id))

    form.datetime.data = editService.datetime
    form.type_.data = editService.type_
    form.category.data = editService.category
    form.desc.data = editService.desc
    form.subject.data = editService.subject
    return render_template('serviceform.html',form=form, service=editService)

@app.route('/serviceselect/<serviceid>/<type_>')
def serviceprovide(serviceid,type_):
    editService = Service.objects.get(pk=serviceid)
    currUser=User.objects.get(pk=session['currUserId'])
    if currUser == editService.applicant or currUser == editService.provider:
        flash("You can't both provide and receive a service.")
        return redirect(url_for('service',serviceid=editService.id))

    if type_=='p':
        editService.update(
            provider=currUser
        )
    elif type_=='a':
        editService.update(
            applicant=currUser
        )
    else:
        flash(f"Something went worng.")
    editService.reload()
    return redirect(url_for('service',serviceid=editService.id))

@app.route('/serviceverify/<serviceid>')
def serviceverify(serviceid):
    service=Service.objects.get(pk=serviceid)
    if not str(service.applicant.id) == str(session['currUserId']):
        flash(f"Only the person who received the service can varify the service was received.")
        return redirect(url_for('service',serviceid=service.id))
    service.update(verified=True)
    service.reload
    return redirect(url_for('service',serviceid=serviceid))

@app.route('/servicedelete/<serviceid>')
def servicedelete(serviceid):
    if not session['admin'] and not str(session['currUserId']) == str(editService.owner.id):
        flash('You are are not the owner of this service.')
        return redirect(url_for('service',serviceid=serviceid))
    delService = Service.objects.get(pk=serviceid)
    delService.delete()
    return redirect(url_for('services'))
