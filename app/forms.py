from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, TextAreaField, DateField, IntegerField, DecimalField, SelectField, PasswordField
from wtforms.validators import DataRequired
import time
import datetime

class LoginForm(Form):
    login = StringField('login', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class CreateCommunityForm(Form):
    title = StringField('title', validators=[DataRequired()])
    desc = StringField('desc')

class SearchCommunityForm(Form):
    query = StringField('query')

class CreateShareForm(Form):
    title = StringField('title', validators=[DataRequired()])
    desc = TextAreaField('desc', validators=[DataRequired()])
    date = DateField('date', default=time, validators=[DataRequired()], format='%m/%d/%Y')
    number_people = IntegerField('number_people', validators=[DataRequired()])
    total_price = DecimalField('total_price', validators=[DataRequired()])
    price_per_people = DecimalField('price_per_people', validators=[DataRequired()])
    community = SelectField('community', choices=[])
