
# -*- coding: utf-8 -*-
"""
The flask application package.
"""
from urllib.parse import urlencode

from flask import Flask
from jinja2 import environment, filters

from table_class.assignment_and_relocation import Assignment_and_relocationIndexEndpoint, \
    Assignment_and_relocationObjectEndpoint
from table_class.kvalif_up import Kvalif_upIndexEndpoint, Kvalif_upObjectEndpoint
from table_class.retraining import RetrainingObjectEndpoint, RetrainingIndexEndpoint
from table_class.user import UsersIndexEndpoint, UsersObjectEndpoint
from table_class.vac_certification import Vac_certificationIndexEndpoint, Vac_certificationObjectEndpoint
from table_class.vacation import VacationIndexEndpoint, VacationObjectEndpoint
from table_class.worker import WorkerIndexEndpoint, WorkerObjectEndpoint

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
from table_class import user, vac_certification

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
worker_resource = Resource('worker', __name__, url_prefix='/worker')
vac_certification_resource = Resource('vac_certification', __name__, url_prefix='/vac-certification')
assignment_and_relocation_resource = Resource('assignment_and_relocation', __name__, url_prefix='/assignment-and-relocation')
vacation_resource = Resource('vacation', __name__, url_prefix='/vacation')
retraining_resource = Resource('retraining', __name__, url_prefix='/retraining')
kvalif_up_resource = Resource('kvalif_up', __name__, url_prefix='/kvalif-up')




users_resource.add_endpoint(UsersIndexEndpoint)
users_resource.add_endpoint(UsersObjectEndpoint)
worker_resource.add_endpoint(WorkerIndexEndpoint)
worker_resource.add_endpoint(WorkerObjectEndpoint)
vac_certification_resource.add_endpoint(Vac_certificationIndexEndpoint)
vac_certification_resource.add_endpoint(Vac_certificationObjectEndpoint)
assignment_and_relocation_resource.add_endpoint(Assignment_and_relocationIndexEndpoint)
assignment_and_relocation_resource.add_endpoint(Assignment_and_relocationObjectEndpoint)
vacation_resource.add_endpoint(VacationIndexEndpoint)
vacation_resource.add_endpoint(VacationObjectEndpoint)
retraining_resource.add_endpoint(RetrainingIndexEndpoint)
retraining_resource.add_endpoint(RetrainingObjectEndpoint)
kvalif_up_resource.add_endpoint(Kvalif_upIndexEndpoint)
kvalif_up_resource.add_endpoint(Kvalif_upObjectEndpoint)



api_v1.register_resource(users_resource)
api_v1.register_resource(worker_resource)
api_v1.register_resource(vac_certification_resource)
api_v1.register_resource(assignment_and_relocation_resource)
api_v1.register_resource(vacation_resource)
api_v1.register_resource(retraining_resource)
api_v1.register_resource(kvalif_up_resource)
