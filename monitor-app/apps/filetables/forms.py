# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FileField, SubmitField
from wtforms.validators import Email, DataRequired


class FiletableForm(FlaskForm):
    type   = SelectField('Type', id='type', choices=[("product", "Product"), ("transaction", "Transaction")], render_kw={'class':'form-select type'})
    name   = StringField('Name', id='name', validators=[DataRequired()], render_kw={'class':'form-control name'})
    value  = StringField('Value', id='value', validators=[DataRequired()], render_kw={'class':'form-control value'})


class UploadFileForm(FlaskForm):
    file = FileField('File')
    submit = SubmitField('Upload File')
