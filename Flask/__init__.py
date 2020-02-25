
# -*- coding: utf-8 -*-
"""
The flask application package.
"""
from urllib.parse import urlencode

from flask import Flask
from jinja2 import environment, filters

from table_class.user import UsersIndexEndpoint, UsersObjectEndpoint


app = Flask(__name__)

import Flask.views

from arrested import (
    ArrestedAPI, Resource, Endpoint, GetListMixin, CreateMixin,
    GetObjectMixin, PutObjectMixin, DeleteObjectMixin, ResponseHandler
)

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine, DateTime

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import sessionmaker
#from kim import field
from table_class import user

from config import SQLALCHEMY_DB_URI

api_v1 = ArrestedAPI(app,url_prefix="/v1")
app.config["SQLALCHEMY_DB_URI"] = SQLALCHEMY_DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

engine = create_engine(app.config['SQLALCHEMY_DB_URI'], echo=True)
metadata = MetaData()

Base = declarative_base()


Session = sessionmaker(bind=engine)
session = Session()

users_resource = Resource('user', __name__, url_prefix='/user')




users_resource.add_endpoint(UsersIndexEndpoint)
users_resource.add_endpoint(UsersObjectEndpoint)



api_v1.register_resource(users_resource)
