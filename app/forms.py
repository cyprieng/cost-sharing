from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, TextAreaField, DateTimeField, IntegerField, DecimalField, SelectField, PasswordField, RadioField
from wtforms.validators import DataRequired
import time
import datetime

class LoginForm(Form):
    """ Form for the login page """
    email = StringField('email', validators=[DataRequired()])
    create = RadioField('Already registered?', choices=[('0','Login'),('1','Create an account')], default='0')
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class CreateCommunityForm(Form):
    """ Form for the create community page """
    title = StringField('title', validators=[DataRequired()])
    desc = StringField('desc')

class SearchCommunityForm(Form):
    """ Form to search in community """
    query = StringField('query')

class CreateShareForm(Form):
    """ Form for the create share page """
    title = StringField('title', validators=[DataRequired()])
    desc = TextAreaField('desc', validators=[DataRequired()])
    date = DateTimeField('date', default=time, validators=[DataRequired()], format='%m/%d/%Y %I:%M %p')
    number_people = IntegerField('number_people', validators=[DataRequired()])
    total_price = DecimalField('total_price', validators=[DataRequired()])
    price_per_people = DecimalField('price_per_people', validators=[DataRequired()])
    community = SelectField('community', choices=[])

class SettingsForm(Form):
    """ Form for the settings page """
    email = StringField('email', validators=[DataRequired()])
    nickname = StringField('nickname', validators=[DataRequired()])
    old_password = PasswordField('old_password')
    new_password1 = PasswordField('new_password1')
    new_password2 = PasswordField('new_password2')

class MoneyForm(Form):
    """ Form for the money page """
    amount = IntegerField('amount', validators=[DataRequired()])
