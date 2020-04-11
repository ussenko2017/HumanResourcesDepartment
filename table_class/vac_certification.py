from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy.orm import sessionmaker
from arrested import (
    ArrestedAPI, Resource, Endpoint, GetListMixin, CreateMixin,
    GetObjectMixin, PutObjectMixin, DeleteObjectMixin, ResponseHandler
)
from config import SQLALCHEMY_DB_URI


engine = create_engine(SQLALCHEMY_DB_URI, echo=True)
metadata = MetaData()
Session = sessionmaker(bind=engine)
session = Session()
class DBResponseHandler(ResponseHandler):

    def __init__(self, endpoint, *args, **params):
        super(DBResponseHandler, self).__init__(endpoint, *args, **params)

        self.serializer = params.pop('serializer', None)

    def handle(self, data, **kwargs):

        if isinstance(data, list):
            objs = []
            for obj in data:
                objs.append(self.serializer(obj))
            return objs
        else:
            return self.serializer(data)



class Vac_certification(Base):
    __tablename__ = 'vac_certification'
            # 7. Аттестация


    id = Column(Integer(), primary_key=True)
    worker_id = Column(Integer(), nullable=False)
    date = Column(String(20),)#Дата
    result_com = Column(String(200),)# Решение комиссии


    date_create = Column(DateTime(), )
    date_edit = Column(DateTime(), )
    creator_id = Column(Integer(), )
    editor_id = Column(Integer(), )
    active = Column(Boolean, nullable=False)  # Активность записи

    def __init__(self,worker_id,date,result_com,  date_create, date_edit, creator_id, editor_id, active):
        self.worker_id = worker_id
        self.date = date
        self.result_com = result_com


        self.date_create = date_create
        self.date_edit = date_edit
        self.creator_id = creator_id
        self.editor_id = editor_id
        self.active = active

    def __repr__(self):
            return "<Vac_certification('%s','%s','%s', '%s', '%s', '%s', '%s', '%s')>" % \
                   (self.worker_id, self.date,self.result_com,
                    self.date_create, self.date_edit, self.creator_id, self.editor_id,
                                                                        self.active)

def table_serializer(obj):
    return {
        'id': obj.id,
        'worker_id':obj.worker_id,
        'date': obj.date,
        'result_com': obj.result_com,
        'date_create':obj.date_create,
        'date_edit':obj.date_edit,
        'creator_id':obj.creator_id,
        'editor_id':obj.editor_id,
        'active':obj.active

    }



class Vac_certificationIndexEndpoint(Endpoint, GetListMixin, CreateMixin):

    name = 'list'
    many = True
    response_handler = DBResponseHandler


    def get_response_handler_params(self, **params):
        params['serializer'] = table_serializer
        return params

    def get_objects(self):

        table = session.query(Vac_certification).all()
        return table

    def save_object(self, obj):

        table = Vac_certification(**obj)
        Base.session.add(Vac_certification)
        session.commit()
        return table


class Vac_certificationObjectEndpoint(Endpoint, GetObjectMixin,
                              PutObjectMixin, DeleteObjectMixin):

    name = 'object'
    url = '/<string:obj_id>'
    response_handler = DBResponseHandler

    def get_response_handler_params(self, **params):

        params['serializer'] = table_serializer
        return params

    def get_object(self):

        obj_id = self.kwargs['obj_id']
        obj = session.query(Vac_certification).filter(Vac_certification.id == obj_id).one_or_none()
        if not obj:
            payload = {
                "message": "Users object not found.",
            }
            self.return_error(404, payload=payload)

        return obj

    def update_object(self, obj):

        data = self.request.data
        allowed_fields = ['worker_id','date','result_com','date_create', 'date_edit', 'creator_id', 'editor_id', 'active']

        for key, val in data.items():
            if key in allowed_fields:
                setattr(obj, key, val)

        session.add(obj)
        session.commit()

        return obj

    def delete_object(self, obj):

        session.delete(obj)
        session.commit()

Base.metadata.create_all(engine)