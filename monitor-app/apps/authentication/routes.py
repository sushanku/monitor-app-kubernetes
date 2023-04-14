# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from uuid import uuid4
from itsdangerous import URLSafeSerializer

from flask import current_app

from flask import render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_user,
    logout_user
)


from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import (LoginForm, CreateAccountForm,
                                       ForgotPasswordForm, ResetPasswordForm)
from apps.authentication.models import Users

from apps.authentication.util import verify_pass, hash_pass

from apps.config import Config
from apps.authentication.email import send_email

@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))

# Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = Users.query.filter_by(username=username).first()

        if user and not user.account_status:
            # Email not confirmed
            return render_template('accounts/login.html',
                                   msg='Inactive account - Please confirm email address',
                                   form=login_form)

        # Check the password
        if user and verify_pass(password, user.password):

            login_user(user)
            return redirect(url_for('authentication_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg='Wrong user or password',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)

    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']
        email = request.form['email']
        msg = None   

        # Check usename exists
        user = Users.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Username already registered',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = Users.query.filter_by(email=email).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user
        user = Users(**request.form)

        # check if confirmation email to be sent or not for activating account
        if Config.EMAIL_CONFIRMATION_REQUIRED:

            user.account_status = False 

            if confirm_user_mail(username, email):
                msg='User created, Please confirm your email'
            else:
                msg='User created, but confirmation email cannot be sent.'     

            db.session.add(user)
            db.session.commit()

            return render_template('accounts/register.html',
                                   msg=msg,
                                   success=True,
                                   form=create_account_form)

        else:
            user.account_status = True
            db.session.add(user)
            db.session.commit()

            return render_template('accounts/register.html',
                                   msg='User created please <a href="/login">login</a>',
                                   success=True,
                                   form=create_account_form)

    else:
        return render_template('accounts/register.html', form=create_account_form)


def confirm_user_mail(username, email):

    # create a confirm_account link to send in email
    s = URLSafeSerializer('serliaizer_code')
    key = s.dumps([username, email])
    url = url_for('authentication_blueprint.confirm_account', secretstring=key, _external=True)

    subject = 'Confirm your account'
    body_content = "Please activate your account. <a href='" + url + "'>Click to Activate</a>"

    return send_email(subject, body_content, email)


@blueprint.route('/confirm_account/<secretstring>', methods=['GET', 'POST'])
def confirm_account(secretstring):
    s = URLSafeSerializer('serliaizer_code')
    username, email = s.loads(secretstring)

    user = Users.query.filter_by(username=username).first()
    user.account_status = True
    db.session.add(user)
    db.session.commit()

    #return redirect(url_for("authentication_blueprint.login", msg="Your account was confirmed succsessfully"))
    return render_template('accounts/login.html',
                        msg='Account confirmed successfully.',
                        form=LoginForm())

@blueprint.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    forgot_password_form = ForgotPasswordForm(request.form)
    if 'forgot-password' in request.form:

        # read form data
        email = request.form['email']

        # Locate user
        user = Users.query.filter_by(email=email).first()

        # Check user exists
        if user:

            user.email_token_key = str(uuid4())
            db.session.add(user)
            db.session.commit()

            # create a set_password link to send in email
            url = url_for('authentication_blueprint.reset_password',
                          email=user.email,
                          email_token_key=user.email_token_key,
                          _external=True)

            subject = 'Reset your password'
            body_content = "Please reset your password. <a href='" + url + "'>Click to Reset</a>"

            send_email(subject, body_content, email)

            return render_template('registration/forgot_password.html',
                                   msg='Instructions sent successfully on your email',
                                   success=True,
                                   form=forgot_password_form)

        return render_template('registration/forgot_password.html',
                               msg='No user exists with this email',
                               success=False,
                               form=forgot_password_form)

    return render_template('registration/forgot_password.html', form=forgot_password_form)

def update_password(email, email_token_key, password):

    user = Users.query.filter_by(email_token_key=email_token_key, email=email).first()

    if user:
        user.password = hash_pass(password)
        user.email_token_key = None
        db.session.add(user)
        db.session.commit()
        return True
    else:
        return False    

@blueprint.route('/reset-password', methods=['GET', 'POST'])
def reset_password():

    email_token_key=request.values["email_token_key"]
    email=request.values["email"]

    current_app.logger.info('RESET_PASS -> EMAIL: ' + email )
    current_app.logger.info('RESET_PASS -> TOKEN: ' + email_token_key )

    user = Users.query.filter_by(email_token_key=email_token_key, email=email).first()
    if user:
        reset_password_form = ResetPasswordForm(email_token_key=email_token_key,
                                                email=email)

        msg=None     
        if 'reset-password' in request.form:
            
            if update_password(reset_password_form.email.data,
                               reset_password_form.email_token_key.data,
                               reset_password_form.password.data):

                msg='Password successfully updated.'
            else:
                msg='Error updating password.'

            #return redirect(url_for("authentication_blueprint.login", msg="Your password has been changed, log in again"))
            return render_template('accounts/login.html',
                        msg=msg,
                        form=LoginForm())

    return render_template("registration/reset_password.html", form=ResetPasswordForm(email_token_key=email_token_key, email=email))

@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))


# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
