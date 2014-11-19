from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from .forms import LoginForm, CreateCommunityForm, SearchCommunityForm, CreateShareForm
from .models import User, Community, Share
import hashlib

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
                user = User(email=email, password=password)
                db.session.add(user)
                db.session.commit()
            else:
                return render_template('login.html',
                                       title='Sign In',
                                       form=form)
        elif user is None:
            return render_template('login.html',
                                   title='Sign In',
                                   form=form)
        elif not user.password == hashlib.md5(form.password.data.encode('utf-8')).hexdigest():
            return render_template('login.html',
                                   title='Sign In',
                                   form=form)


        remember_me = False
        if 'remember_me' in session:
            remember_me = session['remember_me']
            session.pop('remember_me', None)

        login_user(user, remember = remember_me)
        return redirect(request.args.get('next') or url_for('index'))
    return render_template('login.html',
                           title='Sign In',
                           form=form)

@app.before_request
def before_request():
    g.user = current_user

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

            db.session.commit()

    return render_template('create_community.html',
                           title='Create a Community',
                           form=form)

@app.route('/list_community', methods=['GET', 'POST'])
@login_required
def list_community():
    if request.args.get('join') and request.args.get('join').isdigit():
        community = Community.query.filter_by(id=request.args.get('join')).first()
        community.addMember(g.user)
        db.session.add(community)
        db.session.commit()
        return redirect(url_for('list_community'))

    if request.args.get('leave') and request.args.get('leave').isdigit():
        community = Community.query.filter_by(id=request.args.get('leave')).first()
        community.removeMember(g.user)
        db.session.commit()
        return redirect(url_for('list_community'))

    if request.args.get('remove') and request.args.get('remove').isdigit():
        community = Community.query.filter_by(id=request.args.get('remove')).first()
        community.delete(g.user)
        db.session.commit()
        return redirect(url_for('list_community'))

    form = SearchCommunityForm()
    communities = Community.query.all()

    return render_template('list_community.html',
                           title='List of Community',
                           user=g.user,
                           form=form,
                           communities=communities)

@app.route('/list_demand', methods=['GET', 'POST'])
@login_required
def list_demand():
    if request.args.get('accept') and request.args.get('accept').isdigit() and request.args.get('community') and request.args.get('community').isdigit():
        community = Community.query.filter_by(id=request.args.get('community')).first()
        user = User.query.filter_by(id=request.args.get('accept')).first()
        community.validateUser(user)
        db.session.commit()
        return redirect(url_for('list_demand'))

    communities = g.user.communities_owner

    return render_template('list_demand.html',
                           title='List of Demand',
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
                           form=form)
