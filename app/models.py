from app import db
import hashlib

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    shares = db.relationship('Share', backref='author', lazy='dynamic')
    community_owner = db.relationship('Community', backref='owner', lazy='dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (hashlib.md5(self.email.encode('utf-8')).hexdigest(), size)

    def __repr__(self):
        return '<User %r>' % (self.nickname)

class Share(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(140))
    desc = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)
    number_people = db.Column(db.SmallInteger)
    price_total = db.Column(db.SmallInteger)
    price_per_share = db.Column(db.SmallInteger)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    community_id = db.Column(db.Integer, db.ForeignKey('community.id'))

    def __repr__(self):
        return '<Share %r>' % (self.title)

class Community(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(140))
    desc = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    shares = db.relationship('Share', backref='community', lazy='dynamic')

    def __repr__(self):
        return '<Community %r>' % (self.title)
