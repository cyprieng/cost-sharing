from app import db
import hashlib
import time
import datetime

class User(db.Model):
    """ Class representing an user """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(64))
    nickname = db.Column(db.String(120))
    money = db.Column(db.Integer, default=0)
    lastReadNotif = db.Column(db.DateTime, default=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    shares = db.relationship('Share', backref='author', lazy='dynamic')
    communities_owner = db.relationship('Community', backref='owner', lazy='dynamic')
    shares_creator = db.relationship('Share', backref='creator', lazy='dynamic')

    def is_authenticated(self):
        """ Return that the user is authennticated """
        return True

    def is_active(self):
        """ Return that the user is active """
        return True

    def is_anonymous(self):
        """ Return that the user is not anonymous """
        return False

    def get_id(self):
        """ Get the id of the user """
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def avatar(self, size):
        """ Get the link of the user's avatar

        Keyword arguments:
        size -- size of the avatar
        """
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (hashlib.md5(self.email.encode('utf-8')).hexdigest(), size)

    def __repr__(self):
        """ Print user """
        return '<User %r>' % (self.login)

    def getMemberInstance(self, community):
        """ Get the member instance which link the user and the community

        Keyword arguments:
        community -- community to find
        """
        for m in self.memberOf:
            if m.community_id == community.id:
                return m

    def isMember(self, community):
        """ Check if the user is a member in the given community

        Keyword arguments:
        community -- community to check if the user is in it
        """
        for m in self.memberOf:
            if m.community_id == community.id:
                return True

        return False

    def isMemberValidate(self, community):
        """ Check if the user is a validate member in the given community

        Keyword arguments:
        community -- community to check if the user is in it
        """
        for m in self.memberOf:
            if m.community == community and m.validate == True:
                return True

        return False

class Share(db.Model):
    """ Class representing a share """
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
        """ Print the share """
        return '<Share %r>' % (self.title)

class Community(db.Model):
    """ Class representing a community """
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(140))
    desc = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    shares = db.relationship('Share', backref='community', lazy='dynamic')
    members = db.relationship('Member', backref='community', cascade="all, delete-orphan",
                    passive_deletes=True)

    def addMember(self,user):
        """ Add an user to the community

        Keyword arguments:
        user -- user to add
        """
        if not user.isMember(self):
            m = Member(user_id=user.id)
            self.members.append(m)
            return self

    def removeMember(self,user):
        """ Remove the user from the community

        Keyword arguments:
        user -- user to remove
        """
        for m in self.members:
            if m.user_id == user.id:
                db.session.delete(m)

    def delete(self, user):
        """ Delete the community

        Keyword arguments:
        user -- user who is deleting the community
        """
        if user == self.owner: #Check authorization
            db.session.delete(self)

    def validateUser(self, user):
        """ Validate the user in the community

        Keyword arguments:
        user -- user to validate
        """
        if user.isMember(self) and not user.isMemberValidate(self):
            user.getMemberInstance(self).validate = True
            return self

    def __repr__(self):
        """ Print the community """
        return '<Community %r>' % (self.title)

class Member(db.Model):
    """ Represent association between user and community """
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), primary_key=True)
    community_id = db.Column(db.Integer, db.ForeignKey('community.id', ondelete="CASCADE"), primary_key=True)
    validate = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref='memberOf')

class JoinShare(db.Model):
    """ Represent association between user and share """
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), primary_key=True)
    share_id = db.Column(db.Integer, db.ForeignKey('share.id', ondelete="CASCADE"), primary_key=True)
    user = db.relationship('User', backref='joinShare')
    share = db.relationship('Share', backref='people_in')

class Notification(db.Model):
    """ Represent notification """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    msg = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)
    user = db.relationship('User', backref='notifications')

    def add(user, msg):
        """ Add notification

        Keyword arguments:
        user -- user to notify
        msg -- text of the notification
        """
        notif = Notification(user_id=user, msg=msg, timestamp=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        db.session.add(notif)
