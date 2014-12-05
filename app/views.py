from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from .forms import LoginForm, CreateCommunityForm, SearchCommunityForm, CreateShareForm, SettingsForm, MoneyForm
from .models import User, Community, Share, JoinShare, Notification
import hashlib
import urllib.request
import re
import datetime
import time

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = g.user
    members = user.memberOf
    return render_template('index.html',
                           title='Home',
                           notif=g.notif.msg,
                           user=user,
                           members=members)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data

        user = User.query.filter_by(email=form.email.data).first()
        if form.create.data == '1':
            if user is None:
                email = form.email.data
                password = hashlib.md5(form.password.data.encode('utf-8')).hexdigest()
                user = User(email=email, password=password, nickname = email.split('@')[0])
                db.session.add(user)
                db.session.commit()
            else:
                return render_template('login.html',
                                       title='Sign In',
                                       notif=g.notif.msg,
                                       form=form)
        elif user is None:
            return render_template('login.html',
                                   title='Sign In',
                                   form=form)
        elif not user.password == hashlib.md5(form.password.data.encode('utf-8')).hexdigest():
            return render_template('login.html',
                                   title='Sign In',
                                   notif=g.notif.msg,
                                   form=form)


        remember_me = False
        if 'remember_me' in session:
            remember_me = session['remember_me']
            session.pop('remember_me', None)

        login_user(user, remember = remember_me)
        return redirect(request.args.get('next') or url_for('index'))
    return render_template('login.html',
                           title='Sign In',
                           notif=g.notif.msg,
                           form=form)

@app.before_request
def before_request():
    g.user = current_user
    if(g.user.is_authenticated() and len(g.user.notifications) > 0 and g.user.lastReadNotif < g.user.notifications[-1].timestamp):
        g.notif = g.user.notifications[-1];
        g.user.lastReadNotif = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        db.session.add(g.user)
        db.session.commit()
    else:
        g.notif = Notification(msg="")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/create_community', methods=['GET', 'POST'])
@login_required
def create_community():
    form = CreateCommunityForm()
    if form.validate_on_submit():
        community = Community.query.filter_by(title=form.title.data).first()
        if community is None:
            community = Community(title=form.title.data, desc=form.desc.data, user_id=g.user.id)
            db.session.add(community)
            db.session.commit()
            community.addMember(g.user)
            db.session.add(community)
            db.session.commit()
            community.validateUser(g.user)
            db.session.add(community)

            Notification.add(g.user.id, "You create the community: "+community.title)

            db.session.commit()
            return redirect(url_for('list_community'))

    return render_template('create_community.html',
                           title='Create a Community',
                           notif=g.notif.msg,
                           form=form)

@app.route('/list_community', methods=['GET', 'POST'])
@login_required
def list_community():
    if request.args.get('join') and request.args.get('join').isdigit():
        community = Community.query.filter_by(id=request.args.get('join')).first()
        community.addMember(g.user)
        db.session.add(community)
        Notification.add(g.user.id, "You request access to the community: "+community.title)
        Notification.add(community.owner.id, g.user.nickname+" request access to your community: "+community.title)
        db.session.commit()
        return redirect(url_for('list_community'))

    if request.args.get('leave') and request.args.get('leave').isdigit():
        community = Community.query.filter_by(id=request.args.get('leave')).first()
        community.removeMember(g.user)
        Notification.add(g.user.id, "You leave the community: "+community.title)
        db.session.commit()
        return redirect(url_for('list_community'))

    if request.args.get('remove') and request.args.get('remove').isdigit():
        community = Community.query.filter_by(id=request.args.get('remove')).first()
        community.delete(g.user)
        Notification.add(g.user.id, "You removed the community: "+community.title)
        db.session.commit()
        return redirect(url_for('list_community'))

    form = SearchCommunityForm()
    communities = Community.query.all()

    return render_template('list_community.html',
                           title='List of Community',
                           user=g.user,
                           form=form,
                           notif=g.notif.msg,
                           communities=communities)

@app.route('/list_demand', methods=['GET', 'POST'])
@login_required
def list_demand():
    if request.args.get('accept') and request.args.get('accept').isdigit() and request.args.get('community') and request.args.get('community').isdigit():
        community = Community.query.filter_by(id=request.args.get('community')).first()
        user = User.query.filter_by(id=request.args.get('accept')).first()
        community.validateUser(user)
        Notification.add(user.id, "You have been accepted in the community: "+community.title)
        db.session.commit()
        return redirect(url_for('list_demand'))

    communities = g.user.communities_owner

    return render_template('list_demand.html',
                           title='List of Demand',
                           notif=g.notif.msg,
                           communities=communities)

@app.route('/create_share', methods=['GET', 'POST'])
@login_required
def create_share():
    form = CreateShareForm()
    form.community.choices = []
    for m in g.user.memberOf:
        if m.validate:
            form.community.choices.append((str(m.community_id), m.community.title))

    if form.validate_on_submit():
        if g.user.isMemberValidate(Community.query.filter_by(id=form.community.data).first()):
            share = Share(title=form.title.data, desc=form.desc.data, timestamp=form.date.data, number_people=form.number_people.data, price_total=form.total_price.data, price_per_people=form.price_per_people.data, user_id=g.user.id, community_id=form.community.data)
            db.session.add(share)
            db.session.commit()
            return redirect(url_for('index'))


    return render_template('create_share.html',
                           title='Create a Share',
                           notif=g.notif.msg,
                           form=form)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()

    if form.validate_on_submit():
        g.user.email = form.email.data
        g.user.nickname = form.nickname.data

        if not (form.old_password.data == "" or form.new_password1.data == "" or form.new_password2.data == ""):
            if hashlib.md5(form.old_password.data.encode('utf-8')).hexdigest() == g.user.password:
                if form.new_password1.data == form.new_password2.data:
                    g.user.password = hashlib.md5(form.new_password1.data.encode('utf-8')).hexdigest()

        db.session.add(g.user)
        db.session.commit()
        return redirect(url_for('settings'))

    form.email.data = g.user.email
    form.nickname.data = g.user.nickname

    return render_template('settings.html',
                           title='Settings',
                           notif=g.notif.msg,
                           form=form)

@app.route('/share/<share_id>', methods=['GET', 'POST'])
@login_required
def share(share_id):
    share = Share.query.filter_by(id=share_id).first()
    alreadyIn = len(JoinShare.query.filter_by(user_id=g.user.id, share_id=share_id).all()) > 0
    if not g.user.isMemberValidate(share.community):
        return render_template('index.html',
                               title="Home",
                               notif=g.notif.msg,
                               form=form)

    return render_template('share.html',
                           title=share.title,
                           alreadyIn=alreadyIn,
                           notif=g.notif.msg,
                           share=share)

@app.route('/money', methods=['GET', 'POST'])
@login_required
def money():
    form = MoneyForm()
    if form.validate_on_submit():
        s = urllib.request.urlopen("https://api-3t.sandbox.paypal.com/nvp?USER=cyprien.guillemot-facilitator_api1.gmail.com&PWD=KBH5YU4GQ5PGX7P8&SIGNATURE=AVzv9iWQ4Tuaj7RRRQA.nVMPylGdAm5oVB57eq7Saxhu69Prw5.cGRpL&METHOD=SetExpressCheckout&VERSION=78&PAYMENTREQUEST_0_PAYMENTACTION=SALE&PAYMENTREQUEST_0_AMT="+str(form.amount.data)+"&PAYMENTREQUEST_0_CURRENCYCODE=USD&cancelUrl="+url_for('money', _external=True)+"&returnUrl="+url_for('payment', amount = form.amount.data, _external=True))
        data = s.read().decode('utf-8-sig')

        token = re.sub(r'TOKEN=([^&]*)&.*', r'\1', data)

        return redirect("https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_express-checkout&token="+token)

    return render_template('money.html',
                           title="Money",
                           form=form,
                           notif=g.notif.msg,
                           user=g.user)


@app.route('/payment/<amount>', methods=['GET', 'POST'])
@login_required
def payment(amount):
    s = urllib.request.urlopen("https://api-3t.sandbox.paypal.com/nvp?USER=cyprien.guillemot-facilitator_api1.gmail.com&PWD=KBH5YU4GQ5PGX7P8&SIGNATURE=AVzv9iWQ4Tuaj7RRRQA.nVMPylGdAm5oVB57eq7Saxhu69Prw5.cGRpL&METHOD=DoExpressCheckoutPayment&VERSION=78&TOKEN="+ request.args.get('token')+"&PAYERID="+ request.args.get('PayerID')+"&PAYMENTREQUEST_0_PAYMENTACTION=SALE&PAYMENTREQUEST_0_AMT="+amount+"&PAYMENTREQUEST_0_CURRENCYCODE=USD")
    data = s.read().decode('utf-8-sig')
    if(len(re.findall("ACK=Success",data)) > 0):
        g.user.money = g.user.money + int(amount)
        db.session.add(g.user)
        Notification.add(g.user.id, "You add "+amount+"$ to your account.")
        db.session.commit()

    return redirect(url_for('money'))

@app.route('/joinshare/<share_id>', methods=['GET', 'POST'])
@login_required
def joinshare(share_id):
    share = Share.query.filter_by(id=share_id).first()
    if(g.user.money > share.price_per_people and share.number_people > len(share.people_in)):
        js = JoinShare(user_id=g.user.id, share_id=share_id);
        g.user.money = g.user.money - share.price_per_people
        db.session.add(g.user)
        db.session.add(js)
        Notification.add(g.user.id, "You join the share: "+share.title+". "+str(share.price_per_people)+"$ has been charged on your account.")
        db.session.commit()

    return redirect(url_for('share', share_id = share_id))

@app.route('/leaveshare/<share_id>', methods=['GET', 'POST'])
@login_required
def leaveshare(share_id):
    share = Share.query.filter_by(id=share_id).first()
    alreadyIn = len(JoinShare.query.filter_by(user_id=g.user.id, share_id=share_id).all()) > 0
    if(alreadyIn):
        js = JoinShare.query.filter_by(user_id=g.user.id, share_id=share_id).first()
        g.user.money = g.user.money + share.price_per_people
        db.session.add(g.user)
        db.session.delete(js)
        Notification.add(g.user.id, "You leave the share: "+share.title+". "+str(share.price_per_people)+"$ has been added to your account.")
        db.session.commit()

    return redirect(url_for('share', share_id = share_id))

@app.route('/your_share', methods=['GET', 'POST'])
@login_required
def your_share():
    shares = g.user.shares_creator
    sharesIn = g.user.joinShare

    return render_template('your_share.html',
                           title="Your share",
                           shares=shares,
                           notif=g.notif.msg,
                           sharesIn=sharesIn)

@app.route('/remove_share/<share_id>', methods=['GET', 'POST'])
@login_required
def remove_share(share_id):
    share = Share.query.filter_by(id=share_id).first()
    for js in share.people_in:
        js.user.money += share.price_per_people
        db.session.add(js.user)
        db.session.delete(js)
        Notification.add(js.user.id, "The share "+share.title+" has been removed")

    db.session.delete(share)
    db.session.commit()

    return redirect(url_for('your_share'))

@app.route('/close_share/<share_id>', methods=['GET', 'POST'])
@login_required
def close_share(share_id):
    share = Share.query.filter_by(id=share_id).first()
    share.closed = True
    db.session.add(share)
    share.creator.money += len(share.people_in) * share.price_per_people
    db.session.add(share.creator)

    for js in share.people_in:
        Notification.add(js.user.id, "The share "+share.title+" has been closed")

    db.session.commit()

    return redirect(url_for('your_share'))

@app.route('/notification', methods=['GET', 'POST'])
@login_required
def notification():
    notifications = reversed(g.user.notifications)

    return render_template('notifications.html',
                           title="Notification",
                           notif=g.notif.msg,
                           notifications=notifications)
