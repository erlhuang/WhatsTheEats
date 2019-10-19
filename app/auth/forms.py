from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from flask_babel import _, lazy_gettext as _l
from app.models import User
import re

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])


    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('That username is already in use')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('That email address is already in use')
        if 'ucsc.edu' not in email.data:
            raise ValidationError('Please use a valid ucsc.edu email')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class ListingForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    imageurl = StringField('Image URL', validators=[DataRequired()])
    acronym = StringField('Acronym', validators=[DataRequired()])
    timeopen = StringField('Weekday', validators=[DataRequired()])
    timeopen2 = StringField('Weekend hours', validators=[DataRequired()])
    addedInfo = StringField('Description')
    isRestaurant = BooleanField('Restaurant?')
    submit = SubmitField('Add Listing')

class ItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    acronym = StringField('Acronym', validators=[DataRequired()])
    itemURL = StringField('Nutrition URL', validators=[DataRequired()])
    imageurl = StringField('Image URL')
    submit = SubmitField('Add Item')

class AutomateForm(FlaskForm):
    submit = SubmitField('Crawl C9')
