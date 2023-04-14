# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

from datetime import datetime

from flask import render_template, redirect, request, url_for
from flask_login import login_required, current_user

from apps import db
from apps.profile import blueprint
from apps.profile.forms import ProfileForm
from apps.profile.models import Profiles
from apps.profile.util import allowed_image_file

from apps.config import Config


@blueprint.route('/settings/photo/<filename>', methods=['GET', 'POST'])
@login_required
def profile_photo(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


@blueprint.route('/settings.html', methods=['GET', 'POST'])
@login_required
def settings():

    profile_exists = Profiles.query.filter_by(users_id=current_user.id).first()

    if not profile_exists:

        profile_form = ProfileForm()
        user_profile = Profiles()

        if 'profile' in request.form:

            # check if file added and then upload
            file = request.files['photo']
            if file and allowed_image_file(file.filename):
                # create a secure filename and save file in Uploads folder
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = str(current_user.id) + "." + ext
                file.save(os.path.join(Config.basedir + Config.UPLOAD_FOLDER, filename))

            profile_form.populate_obj(user_profile)

            user_profile.users_id = current_user.id
            # convert date str into python datetime object
            user_profile.birthday = datetime.strptime(request.form['birthday'], '%m/%d/%Y')

            # add saved filename into user profile column
            if file and allowed_image_file(file.filename):
                user_profile.photo = filename
            else:
                user_profile.photo = ""

            db.session.add(user_profile)
            db.session.commit()

            return render_template('profile/settings.html',
                                   form=profile_form,
                                   msg='Profile details added successfully',
                                   segment='profile')

        return render_template('profile/settings.html', form=profile_form, segment='profile')

    if profile_exists:

        profile_form = ProfileForm(obj=profile_exists)

        if 'profile' in request.form:

            # check if file added and upload
            file = request.files['photo']
            if file and allowed_image_file(file.filename):
                # create a secure filename and save file in Uploads folder
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = str(current_user.id) + "." + ext
                print(filename)
                file.save(os.path.join(Config.basedir + Config.UPLOAD_FOLDER, filename))

            profile_form.populate_obj(profile_exists)

            # convert date str into python datetime object
            profile_exists.birthday = datetime.strptime(request.form['birthday'], '%m/%d/%Y')

            # add saved filename into user profile column
            if file and allowed_image_file(file.filename):
                profile_exists.photo = filename
            else:
                profile_exists.photo = ""

            db.session.add(profile_exists)
            db.session.commit()

            return render_template('profile/settings.html',
                                   form=profile_form,
                                   msg='Profile details updated successfully',
                                   segment='profile')

        return render_template('profile/settings.html', form=profile_form, segment='profile')

    return redirect(url_for('home_blueprint.index'))
