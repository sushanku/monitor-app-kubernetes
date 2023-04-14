# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FileField
from wtforms.validators import Email, DataRequired

# user profile

class ProfileForm(FlaskForm):
    firstname  = StringField('First Name', id='first_name', validators=[DataRequired()])
    lastname   = StringField('Last Name', id='last_name', validators=[DataRequired()])
    birthday   = StringField('Birthday', id='birthday', validators=[DataRequired()])
    gender     = SelectField('Gender', id='gender', choices=[("1", "Male"), ("2", "Female")])
    email      = StringField('Email', id='email', validators=[DataRequired(), Email()])
    phone      = StringField('Phone', id='phone', validators=[DataRequired()])
    address    = StringField('Address', id='address', validators=[DataRequired()])
    number     = StringField('Number', id='number', validators=[DataRequired()])
    city       = StringField('City', id='city', validators=[DataRequired()])
    state      = StringField('State', id='state', validators=[DataRequired()])
    country    = StringField('Country', id='country', validators=[DataRequired()])
    zipcode    = StringField('Zip Code', id='zipcode', validators=[DataRequired()])
    photo      = FileField('Profile Photo', id='photo', validators=[DataRequired()])
