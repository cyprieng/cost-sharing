from app import db
import hashlib

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(64))
    nickname = db.Column(db.String(120))
    money = db.Column(db.Integer, default=0)
    shares = db.relationship('Share', backref='author', lazy='dynamic')
    communities_owner = db.relationship('Community', backref='owner', lazy='dynamic')
    shares_creator = db.relationship('Share', backref='creator', lazy='dynamic')

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
        return '<User %r>' % (self.login)

    def getMemberInstance(self, community):
        for m in self.memberOf:
            if m.community_id == community.id:
                return m

    def isMember(self, community):
        for m in self.memberOf:
            if m.community_id == community.id:
                return True

        return False

    def isMemberValidate(self, community):
        for m in self.memberOf:
            if m.community == community and m.validate == True:
                return True

        return False

class Share(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(140))
    desc = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)
    number_people = db.Column(db.SmallInteger)
    price_total = db.Column(db.SmallInteger)
    price_per_people = db.Column(db.SmallInteger)
    closed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    community_id = db.Column(db.Integer, db.ForeignKey('community.id', ondelete="CASCADE"))

    def __repr__(self):
        return '<Share %r>' % (self.title)

class Community(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(140))
    desc = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    shares = db.relationship('Share', backref='community', lazy='dynamic')
    members = db.relationship('Member', backref='community', cascade="all, delete-orphan",
                    passive_deletes=True)

    def addMember(self,user):
        if not user.isMember(self):
            m = Member(user_id=user.id)
            self.members.append(m)
            return self

    def removeMember(self,user):
        for m in self.members:
            if m.user_id == user.id:
                db.session.delete(m)

    def delete(self, user):
        if user == self.owner:
            db.session.delete(self)

    def validateUser(self, user):
        if user.isMember(self) and not user.isMemberValidate(self):
            user.getMemberInstance(self).validate = True
            return self

    def __repr__(self):
        return '<Community %r>' % (self.title)

class Member(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), primary_key=True)
    community_id = db.Column(db.Integer, db.ForeignKey('community.id', ondelete="CASCADE"), primary_key=True)
    validate = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref='memberOf')

class JoinShare(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), primary_key=True)
    share_id = db.Column(db.Integer, db.ForeignKey('share.id', ondelete="CASCADE"), primary_key=True)
    user = db.relationship('User', backref='joinShare')
    share = db.relationship('Share', backref='people_in')

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    msg = db.Column(db.Text)
    user = db.relationship('User', backref='notifications')

    def add(user, msg):
        notif = Notification(user_id=user, msg=msg)
        db.session.add(notif)
