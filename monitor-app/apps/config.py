# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
from decouple import config

class Config(object):

    basedir = os.path.abspath(os.path.dirname(__file__))

    DB_ENGINE = os.environ.get("DB_ENGINE")
    DB_HOST = os.environ.get("DB_HOST")
    DB_PORT = os.environ.get("DB_PORT")
    DB_NAME = os.environ.get("DB_NAME")
    DB_USERNAME = os.environ.get("DB_USERNAME")
    DB_PASS = os.environ.get("DB_PASS")
    SECRET_KEY = os.environ.get("SECRET_KEY")

    # Set up the App SECRET_KEY
    SECRET_KEY = config('SECRET_KEY')

    # This will create a file in <app> FOLDER
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Profile image upload
    UPLOAD_FOLDER = "/static/uploads/"
    MAX_CONTENT_LENGTH = 1024 * 1024

    ## File upload
    FILE_UPLOAD_FOLDER = "/static/file_uploads"


    # Check if Email confirmation is required or not
    EMAIL_CONFIRMATION_REQUIRED = False  # Or True, if emails to be sent

    # SMTP server credentials
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 465
    MAIL_USERNAME = "abcexample@gmail.com"
    MAIL_PASSWORD = "abc12345"
    MAIL_USE_TSL = False
    MAIL_USE_SSL = True


class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

    # PostgreSQL database
    SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
        config('DB_ENGINE'),
        config('DB_USERNAME'),
        config('DB_PASS'),
        config('DB_HOST'),
        config('DB_PORT'),
        config('DB_NAME')
    )



class DebugConfig(Config):
    DEBUG = False


# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}
