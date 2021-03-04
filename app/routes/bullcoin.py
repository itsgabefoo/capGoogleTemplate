from app import app
from flask import render_template, redirect, url_for, session, flash
from app.classes.data import User, Bullcoin, Service, Approval
from app.classes.forms import ServiceForm
from .users import *
import datetime as dt
# from bson.objectid import ObjectId
   
def transaction(giver,getter,numCoins,source=None):
    coinsGiven=0 
    coinsNotGiven=0

    # TODO put this in app.before_first_request and store to DB in a settings table
    bankUser = User.objects.get(pk=bankUserId)
    currUser=User.objects.get(pk=session['currUserId'])

    if giver == getter:
        status="Fail"
        flash(f"The giver and the getter are the same user.")
        return status

    # this transaction can proceed if the current user is the giver or
    # the giver is the bankUser and the current user is a banker
    if currUser == giver or (currUser.banker and giver == bankUser):
        coins=Bullcoin.objects(owner=giver).limit(numCoins)
        if len(coins) < numCoins:
            flash(f"{giver.fname} {giver.lname} does not have enough coins to complete this transaction.")
            status='fail'
            return status
        for coin in coins:
            # create empty list from coins to be put in approval queue         
            # give the coin to the getter
            coin.update(
                owner = getter
                )
            giver.gavecoins.append(getter)
            getter.gotcoins.append(giver)
        giver.save()
        getter.save()
        flash(f"{giver.fname} {giver.lname} gave {numCoins} Bullcoin to {getter.fname} {getter.lname}")
        status="success"
    else:
        # approvals are transactions that are waiting to be sent to the transaction 
        # function by a banker 
        newApproval = Approval(
                giver=giver,
                getter=getter,
                numcoins=numCoins,
                status="Pending",
                source=source
            )
        newApproval.save()
        flash(f"The transaction has been sent to the Bankers to be approved. Please check back later.")
        status="pending"
    return status


@app.route('/admin')
def admin():
    currUser = User.objects.get(pk = session['currUserId'])
    bankUser = User.objects.get(pk=bankUserId)
    if currUser.banker:
        numBankCoins = Bullcoin.objects(owner=bankUser).count()
        numTotalCoins = Bullcoin.objects().count()

        # this is a mongodb aggregation that groups by the owner field and then counts the number of records in each group
        pipeline=[{ "$group" : { "_id": "$owner", "count" : { "$sum" : 1 } } }]
        coinOwners = Bullcoin.objects().aggregate(pipeline)

        # need to get the User object from the ObjectId that is the result of the aggregation operation
        coinOwnersDisplay = []
        for coinOwner in coinOwners:
            if coinOwner['_id'] == bankUser:
                coinOwner['_id'] = "Bank"
            else:
                coinOwner['_id'] = User.objects.get(pk=coinOwner['_id'])
            coinOwnersDisplay.append(coinOwner)

        approvals = Approval.objects()

        return render_template("admin.html", numBankCoins=numBankCoins, numTotalCoins=numTotalCoins, coinOwners=coinOwnersDisplay, approvals=approvals)
    else:
        flash(f"You are not a banker. If this is wrong, logout and log back in again.")
        return redirect('profile')

@app.route('/coinmint/<amt>')
def coinmint(amt):
    currUser = User.objects.get(pk = session['currUserId'])
    bankUser = User.objects.get(pk=bankUserId)
    if currUser.banker:
        amt = int(amt)
        numBankCoins = Bullcoin.objects(owner=None).count()
        if amt > 0:
            for n in range(amt):
                Bullcoin(owner=bankUser).save()
            flash(f"{abs(amt)} Bullcoins Created.")
        elif amt < 0:
            if numBankCoins >= abs(amt):
                delBullcoins = Bullcoin.objects(owner=bankUser).limit(abs(amt))
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
    bankUser = User.objects.get(pk=bankUserId)
    if currUser.banker:
        amt = int(amt)
        numBankCoins = Bullcoin.objects(owner=bankUser).count()
        getter = User.objects.get(email=useremail)
        if amt > numBankCoins:
            flash(f"The bank has {numBankCoins} coins but you asked for {amt}.")

        # Give coins from the bank to the user
        elif amt > 0:
            giveBankCoins = Bullcoin.objects(owner=bankUser).limit(amt)
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
                    owner = bankUser
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
    # Create a list of users allowed to edit this record
    editors=[editService.owner.id]
    if editService.applicant:
        editors.append(editService.applicant.id)
    if editService.provider:
        editors.append(editService.provider.id)

    if not session['banker'] and not str(session['currUserId']) in str(editors):
        flash("You can't edit this service.")
        return redirect(url_for('service',serviceid=editService.id))

    form = ServiceForm()
    if form.validate_on_submit():

        currUser=User.objects.get(pk=session['currUserId'])

        if form.type_.data=="Provider" and not editService.provider:
            editService.update(provider=currUser)

        elif form.type_.data=="Applicant" and not editService.provider:
            editService.update(applicant=currUser)

        editService.update(
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

    if type_=='p' and editService.provider==None:
        editService.update(
            provider=currUser
        )
    elif type_=='a' and editService.applicant==None:
        editService.update(
            applicant=currUser
        )
    else:
        flash(f"Something went worng. Most likely you applied for a role (pROVIDER OR applicant) that is already selected.")

    editService.reload()
    return redirect(url_for('service',serviceid=editService.id))

@app.route('/serviceverify/<serviceid>')
def serviceverify(serviceid):
    service=Service.objects.get(pk=serviceid)
    print(service.datetime < dt.datetime.utcnow())
    if service.verified==True:
        flash(f"This service is already verified.")
    elif not service.confirmed:
        flash(f"You can't verify a service that has not been confirmed.") 
    elif not service.datetime < dt.datetime.utcnow():
        flash(f"You can't verify a service that has not yet happened.")   
    elif not str(service.applicant.id) == str(session['currUserId']):
        flash(f"Only the person who received the service can varify the service was received.")    
    elif not service.applicant or not service.provider:
        flash(f"There must be both a Provider and an Applicant to verify.")
    else:
        # The service has been verified and the provider and the applicant can get paid
        # get to Bullcoin to give to the applicant
        source=f"/service/{serviceid}"
        bankUser=User.objects.get(pk=bankUserId)
        result1=transaction(bankUser,service.applicant,2,source)
        result2=transaction(bankUser,service.provider,2,source)

        if not result1.lower()=='fail' and not result2.lower()=='fail':
            service.update(verified=True)
            service.reload
            flash(f"Service was successfully verified and Bullcoin was transferred or submitted for approval")
        else:
            flash(f"Service was not verified because Bullcoin could not be transferred.")

    return redirect(url_for('service',serviceid=serviceid))

@app.route('/serviceconfirm/<serviceid>')
def serviceconfirm(serviceid):
    service=Service.objects.get(pk=serviceid)
    currUser=User.objects.get(pk=session['currUserId'])

    if not currUser == service.owner:
        flash(f"You are not the owner of this Service record so you can't confirm it.")

    elif service.datetime > dt.datetime.utcnow() and service.applicant and service.provider:

        # Get two coins to pay the applicant for confirm the help is going to be provided
        bankUser=User.objects.get(pk=bankUserId)
        source=f"/service/{serviceid}"
        status=transaction(bankUser,service.applicant,2,source)

        if not status.lower()=='fail':
            service.update(confirmed=True)
            service.reload()
            flash(f"Service is confirmed to happen on {service.datetime}.")
        else:
            flash(f"Bullcoin was unable to be transferred so service was not confirmed.")
    else:
        flash(f"Service is not confirmed. To be confirmed a service must have three things: a Provider, an Appicant and a Date that occurs in the future.")
        
    return redirect(url_for('service',serviceid=serviceid))

@app.route('/servicedelete/<serviceid>')
def servicedelete(serviceid):
    delService = Service.objects.get(pk=serviceid)
    if not session['admin'] and not str(session['currUserId']) == str(delService.owner.id):
        flash('You are are not the owner of this service.')
        return redirect(url_for('service',serviceid=serviceid))
    delService.delete()
    return redirect(url_for('services'))

@app.route('/transactionapprove/<approvalid>')
def transactionapprove(approvalid):
    approval=Approval.objects.get(pk=approvalid)
    result=transaction(approval.giver,approval.getter,approval.numcoins)
    if result.lower()=='success':
        approval.delete()
        flash(f"Transaction successfully approved")
    else:
        flash(f"Something went wrong")
    return redirect(url_for('admin'))
