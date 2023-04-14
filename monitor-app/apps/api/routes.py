# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from importlib.resources import path
import os
import magic
from flask import request, flash, request, redirect, url_for, jsonify
from flask_restx import Api, Resource, fields, reqparse
import sqlalchemy

from datetime import datetime
from calendar import day_name
from sqlalchemy import desc, asc, extract, func, cast
from pytz import timezone
from werkzeug.utils import secure_filename
from apps.config import Config

from apps import db
from apps.home.models import Fileinfo, UploadFile
from apps.api import rest_api


UPLOAD_FOLDER = '/apps/static/file_uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'])


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def format_timezone(d):
    format = "%Y-%m-%d %H:%M:%S"
    tzInfo = timezone('Asia/Kathmandu')
    date_timezone = d.astimezone(tzInfo).strftime(format)
    return date_timezone

def format_day(d):
    format = "%Y-%m-%d"
    tzInfo = timezone('Asia/Kathmandu')
    date_timezone = d.astimezone(tzInfo).strftime(format)
    day=d.weekday()
    day = day_name[day] + " " + date_timezone
    return day


"""
    Files routes
"""
@rest_api.route('/api/fileinfos')
class Files(Resource):
    """
       Return all items
    """
    def get(self):

        files = UploadFile.query.all()
        file_list = []
        for file in files:
            file.date = format_timezone(file.date)
            file_list.append(file.toJSON())
        return file_list 


@rest_api.route('/api/fileinfos/filetype')
class FilesType(Resource):
    def get(self):
        # filestype = [file[0] for file in UploadFile.query.with_entities(UploadFile.filetype).all()]
        filestype = db.session.query(UploadFile.filetype, db.func.count(UploadFile.filetype)).group_by(UploadFile.filetype).all()
        # filestype_dict = {i:filestype.count(i) for i in filestype}
        filestype_dict = {file[0]:file[1] for file in filestype}
        # filestype_dict = {}
        # for file in filestype:
        #     filestype_dict.update({file[0]: file[1]})
        # print(filestype)
        return filestype_dict


@rest_api.route('/api/fileinfos/all')
class FilesIndex(Resource):
    def get(self):
        month = func.DATE_TRUNC('week', UploadFile.date)
        filesIndex_list = []
        filestype = db.session.query(month, func.count(UploadFile.date)).order_by(month).group_by(month).all()
        filesIndex = [ format_day(file[0]) for file in UploadFile.query.with_entities(UploadFile.date).all()]
        filestype_dict = {}
        for (key, value) in filestype:
            filestype_dict[format_day(key)]= value
        filesIndex_dict = {i:filesIndex.count(i) for i in filesIndex}
        # print(filesIndex_dict)
        for key, value in filesIndex_dict.items():
            filesIndex_list.append({key:value})
            # print(key, value)
        # print(filesIndex_list)
        # return filesIndex_dict
        return filesIndex_dict


@rest_api.route('/api/fileinfos/month')
class FilesIndex(Resource):
    def get(self):
        month = func.DATE_TRUNC('month', UploadFile.date)
        filestype = db.session.query(month, func.count(UploadFile.date)).order_by(month).group_by(month).all()
        filestype_dict = {}
        for (key, value) in filestype:
            filestype_dict[format_day(key)]= value
        return filestype_dict


@rest_api.route('/api/fileinfos/week')
class FilesIndex(Resource):
    def get(self):
        week = func.DATE_TRUNC('week', UploadFile.date)
        filestype = db.session.query(week, func.count(UploadFile.date)).order_by(week).group_by(week).all()
        filestype_dict = {}
        for (key, value) in filestype:
            filestype_dict[format_day(key)]= value
        return filestype_dict


@rest_api.route('/api/fileinfos/day')
class FilesIndex(Resource):
    def get(self):
        day = func.DATE_TRUNC('day', UploadFile.date)
        filestype = db.session.query(day, func.count(UploadFile.date)).order_by(day).group_by(day).all()
        filestype_dict = {}
        for (key, value) in filestype:
            filestype_dict[format_day(key)]= value
        return filestype_dict


parser = reqparse.RequestParser()
parser.add_argument('selected_time', type=str)


@rest_api.route('/api/fileinfos/')
class FilesIndex(Resource):
    @rest_api.doc(parser=parser)
    def get(self):
        args = parser.parse_args()
        selected_time = args["selected_time"]
        print(selected_time)
        week = func.DATE_TRUNC(selected_time, UploadFile.date)
        filestype = db.session.query(week, func.count(UploadFile.date)).order_by(week).group_by(week).all()
        filestype_dict = {}
        for (key, value) in filestype:
            filestype_dict[format_day(key)]= value
        return filestype_dict



@rest_api.route('/api/file_upload')
class FilesUpload(Resource):
    def post(self):
        if 'file' not in request.files:
            resp = jsonify({'message' : 'No file part in the request'})
            resp.status_code = 400
            return resp

        file = request.files['file']
        if file.filename == '':
            resp = jsonify({'message' : 'No file selected for uploading'})
            resp.status_code = 400
            return resp

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(Config.basedir + Config.FILE_UPLOAD_FOLDER, filename)
            file.save(filepath)
            filesize = os.stat(filepath).st_size
            filetype = magic.from_file(filepath, mime=True)
            uploadfile = UploadFile(filename=filename, filetype=filetype, filesize=filesize)
            db.session.add(uploadfile)
            db.session.commit()
            # upload_fileinfo=UploadFile(filename=filename, filetype=filetype, filesize=filesize, path=filepath)
            # db.session.add(upload_fileinfo)
            # db.session.commit()
            resp = jsonify({'message' : 'File successfully uploaded'})
            resp.status_code = 201
            return resp
        else:
            resp = jsonify({'message' : 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
            resp.status_code = 400
            return resp