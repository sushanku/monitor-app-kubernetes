# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps import db

class Profiles(db.Model):

    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)

    firstname = db.Column(db.String(64))
    lastname  = db.Column(db.String(64))
    birthday  = db.Column(db.DateTime)
    gender    = db.Column(db.Integer)
    phone     = db.Column(db.String(32))
    address   = db.Column(db.String(128))
    number    = db.Column(db.String(64))
    city      = db.Column(db.String(64))
    state     = db.Column(db.String(64))
    country   = db.Column(db.String(64))
    zipcode   = db.Column(db.String(16))
    photo     = db.Column(db.String(512))

    users_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship("Users", uselist=False, backref="profiles")

    def __repr__(self):
        return str(self.id)
