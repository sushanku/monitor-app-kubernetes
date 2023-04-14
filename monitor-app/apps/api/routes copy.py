# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import request
from flask_restx import Api, Resource, fields

from apps import db
from apps.home.models import Data, Fileinfo
from apps.api import rest_api

from datetime import datetime
from calendar import day_name
from sqlalchemy import desc, asc
from pytz import timezone

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
    print(day)
    return day


"""
API Interface:
   
   - /data
       - GET: return all items
       - POST: create a new item
   
   - /data/:id
       - GET    : get item
       - PUT    : update item
       - DELETE : delete item
"""

"""
Flask-RestX models Request & Response DATA
"""


# Used to validate input data for creation
create_model = rest_api.model('CreateModel', {"value": fields.String(required=True, min_length=1, max_length=255)})

# Used to validate input data for update
update_model = rest_api.model('UpdateModel', {"value": fields.String(required=True, min_length=1, max_length=255)})

"""
    Flask-Restx routes
"""

@rest_api.route('/api/data')
class Items(Resource):

    """
       Return all items
    """
    def get(self):

        items = Data.query.all()
        
        return {"success" : True,
                "msg"     : "Items found ("+ str(len( items ))+")",
                "datas"   : str( items ) }, 200

    """
       Create new item
    """
    @rest_api.expect(create_model, validate=True)
    def post(self):

        # Read ALL input  
        req_data = request.get_json()

        # Get the information    
        item_value = req_data.get("value")

        # Create new object
        new_item = Data(value=item_value)

        # Save the data
        new_item.save()
        
        return {"success": True,
                "msg"    : "Item successfully created ["+ str(new_item.id)+"]"}, 200

@rest_api.route('/api/data/<int:id>')
class ItemManager(Resource):

    """
       Return Item
    """
    def get(self, id):

        item = Data.get_by_id(id)

        if not item:
            return {"success": False,
                    "msg": "Item not found."}, 400

        return {"success" : True,
                "msg"     : "Successfully return item [" +str(id)+ "]",
                "data"    :  item.toJSON()}, 200

    """
       Update Item
    """
    @rest_api.expect(update_model, validate=True)
    def put(self, id):

        item = Data.get_by_id(id)

        if not item:
            return {"success": False,
                    "msg": "Item not found."}, 400

        # Read input from body  
        req_data = request.get_json()

        # Get the information    
        item_val = req_data.get("value")


        item.update_value(item_val)
        item.save()

        return {"success" : True,
                "msg"     : "Item [" +str(id)+ "] successfully updated",
                "data"    :  item.toJSON()}, 200 

    """
       Delete Item
    """
    def delete(self, id):

        # Locate the Item
        item = Data.get_by_id(id)

        if not item:
            return {"success": False,
                    "msg": "Item not found."}, 400

        # Delete and save the change
        Data.query.filter_by(id=id).delete()
        db.session.commit()

        return {"success" : True,
                "msg"     : "Item [" +str(id)+ "] successfully deleted"}, 200                           

"""
    Sales routes
"""
@rest_api.route('/api/sales')
class Sales(Resource):

    """
       Return all items
    """
    def get(self):

        values = Data.query.with_entities(Data.value, Data.ts).order_by(asc(Data.ts)).all()
        
        sales_total = 0
        date_start  = values[0].ts
        date_end    = values[0].ts

        daily_sales_val = []
        daily_sales_ts  = []
        sales_ts        = {}

        # Iterate on available data
        for sale in values:

            # total sales
            sales_total += sale.value

            # Compute Lowest Date    
            if date_start > sale.ts:
                date_start = sale.ts

            # Compute Highest Date
            if date_end < sale.ts:
                date_end = sale.ts

            day_ts = datetime.utcfromtimestamp(sale.ts).strftime('%m-%d')

            if day_ts not in sales_ts:
                sales_ts[day_ts] = 0

            sales_ts[day_ts] += sale.value

        customers  = len( values )

        # Report Timeframe
        report_timeframe = int ( ( datetime.utcnow().timestamp() - date_start ) / 86400 )

        date_start = datetime.utcfromtimestamp(date_start).strftime('%Y-%m-%d')
        date_end   = datetime.utcfromtimestamp(date_end).strftime('%Y-%m-%d')
        
        # Average order value
        sales_aov  = sales_total / customers

        # Sorted access
        for k, v in sales_ts.items():
            daily_sales_ts.append( k )
            daily_sales_val.append( str( v ) )

        daily_sales_ts  = ", ".join( daily_sales_ts  ) 
        daily_sales_val = ", ".join( daily_sales_val ) 

        return {"success"          : True,
                "msg"              : "Items found ("+ str( customers ) +")",
                "sales_total"      : str( sales_total ), 
                "sales_aov"        : str( sales_aov ), 
                "customers"        : customers,
                "date_start"       : date_start,
                "date_end"         : date_end,
                "report_timeframe" : str(report_timeframe) + " days Timeframe",
                "report_days"      : daily_sales_ts,
                "report_values"    : daily_sales_val
                }, 200



"""
    Files routes
"""
@rest_api.route('/api/fileinfos')
class Files(Resource):
    """
       Return all items
    """
    def get(self):

        files = Fileinfo.query.all()
        file_list = []
        for file in files:
            file.date = format_timezone(file.date)
            file_list.append(file.toJSON())
        return file_list 


@rest_api.route('/api/fileinfos/filetype')
class FilesType(Resource):
    def get(self):
        # filestype = [file[0] for file in Fileinfo.query.with_entities(Fileinfo.filetype).all()]
        filestype = db.session.query(Fileinfo.filetype, db.func.count(Fileinfo.filetype)).group_by(Fileinfo.filetype).all()
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
        filesIndex_list = []
        filesIndex = [ format_day(file[0]) for file in Fileinfo.query.with_entities(Fileinfo.date).all()]
        filesIndex_dict = {i:filesIndex.count(i) for i in filesIndex}
        for key, value in filesIndex_dict.items():
            filesIndex_list.append({key:value})
            # print(key, value)
        # print(filesIndex_list)
        # print(filesIndex_dict)
        return filesIndex_dict


@rest_api.route('/api/fileinfos/month')
class FilesIndex(Resource):
    def get(self):
        filesIndex_list = []
        filesIndex = [ format_timezone(file[0]) for file in Fileinfo.query.with_entities(Fileinfo.date).all()]
        filesIndex_dict = {i:filesIndex.count(i) for i in filesIndex}
        for key, value in filesIndex_dict.items():
            filesIndex_list.append({key:value})
            # print(key, value)
        # print(filesIndex_list)
        # print(filesIndex_dict)
        return filesIndex_dict


@rest_api.route('/api/fileinfos/week')
class FilesIndex(Resource):
    def get(self):
        filesIndex_list = []
        filesIndex = [ format_timezone(file[0]) for file in Fileinfo.query.with_entities(Fileinfo.date).all()]
        filesIndex_dict = {i:filesIndex.count(i) for i in filesIndex}
        for key, value in filesIndex_dict.items():
            filesIndex_list.append({key:value})
            # print(key, value)
        # print(filesIndex_list)
        # print(filesIndex_dict)
        return filesIndex_dict


@rest_api.route('/api/fileinfos/day')
class FilesIndex(Resource):
    def get(self):
        filesIndex_list = []
        filesIndex = [ format_timezone(file[0]) for file in Fileinfo.query.with_entities(Fileinfo.date).all()]
        filesIndex_dict = {i:filesIndex.count(i) for i in filesIndex}
        for key, value in filesIndex_dict.items():
            filesIndex_list.append({key:value})
            # print(key, value)
        # print(filesIndex_list)
        # print(filesIndex_dict)
        return filesIndex_dict




