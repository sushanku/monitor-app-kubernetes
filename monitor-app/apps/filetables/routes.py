# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, request, jsonify, url_for, redirect, session
from sqlalchemy import or_

from apps import db

from apps.filetables import blueprint
from apps.home.models import Fileinfo, UploadFile
from apps.filetables.util import set_pagination

# from apps.filetables.forms import UploadFileForm


@blueprint.route('/file_list.html')
def uploadfiletables():
    if "ITEMS_PER_PAGE" not in session:
        session["ITEMS_PER_PAGE"] = 10

    search = request.args.get("search")
    if search:
        ITEMS_PER_PAGE = session["ITEMS_PER_PAGE"]
        page = request.args.get('page', 1, type=int)

        total_items = UploadFile.query.count()
        print(total_items)
        paginated_data = UploadFile.query.filter(or_(UploadFile.name.like(search), UploadFile.value.like(search))).paginate(page, ITEMS_PER_PAGE, False)
    else:
        ITEMS_PER_PAGE = session["ITEMS_PER_PAGE"]
        page = request.args.get('page', 1, type=int)

        total_items = UploadFile.query.count()
        paginated_data = UploadFile.query.paginate(page, ITEMS_PER_PAGE, False)

    pagination = set_pagination(page, ITEMS_PER_PAGE, total_items, paginated_data)


    return render_template('filetables/file_list.html',
                           file_list=paginated_data.items,
                           pagination=pagination,
                           segment="filetables")

@blueprint.route('/file_delete/<id>', methods=["DELETE"])
def file_delete(id):
    data = UploadFile.query.get(id)
    db.session.delete(data)
    db.session.commit()

    response = {'valid': 'success', 'message': 'Item deleted successfully', 'redirect_url': None}
    return jsonify(response)



# @blueprint.route('/file_list.html')
# def filetables():
#     if "ITEMS_PER_PAGE" not in session:
#         session["ITEMS_PER_PAGE"] = 10

#     search = request.args.get("search")
#     if search:
#         ITEMS_PER_PAGE = session["ITEMS_PER_PAGE"]
#         page = request.args.get('page', 1, type=int)

#         total_items = Fileinfo.query.count()
#         paginated_data = Fileinfo.query.filter(or_(Fileinfo.name.like(search), Fileinfo.value.like(search))).paginate(page, ITEMS_PER_PAGE, False)
#     else:
#         ITEMS_PER_PAGE = session["ITEMS_PER_PAGE"]
#         page = request.args.get('page', 1, type=int)

#         total_items = Fileinfo.query.count()
#         paginated_data = Fileinfo.query.paginate(page, ITEMS_PER_PAGE, False)

#     pagination = set_pagination(page, ITEMS_PER_PAGE, total_items, paginated_data)


#     return render_template('filetables/file_list.html',
#                            file_list=paginated_data.items,
#                            pagination=pagination,
#                            segment="filetables")


# @blueprint.route('/file_delete/<id>', methods=["DELETE"])
# def file_delete(id):
#     data = Fileinfo.query.get(id)
#     db.session.delete(data)
#     db.session.commit()

#     response = {'valid': 'success', 'message': 'Item deleted successfully', 'redirect_url': None}
#     return jsonify(response)


# @blueprint.route('/transactions_rows_per_page/<int:rows>')
# def transactions_rows_per_page(rows):
#     session["ITEMS_PER_PAGE"] = int(rows)
#     return redirect(url_for('datatables_blueprint.transactions'))


# @blueprint.route('/edit/<id>', methods=["GET", "POST"])
# def edit(id):

#     data = Data.query.get(id)
#     form = DatatableForm(obj=data)

#     if form.validate_on_submit():
#         form.populate_obj(data)

#         db.session.add(data)
#         db.session.commit()

#         return redirect(url_for('datatables_blueprint.transactions'))

#     return render_template('datatables/edit.html', form=form, data=data, segment="datatables")