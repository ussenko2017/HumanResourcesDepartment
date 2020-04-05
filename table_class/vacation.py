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



class Vacation(Base):
    __tablename__ = 'vacation'
            # 6. Отпуска


    id = Column(Integer(), primary_key=True)
    worker_id = Column(Integer(), nullable=False)

    period = Column(String(200),)
    osnov = Column(String(200),)# Основание
    kolvo_dney = Column(Integer(),)# кол-во рабочих дней
            #Дополнительный отпуск
    dop_1 = Column(String(100),)
    dop_2 = Column(String(100),)
    dop_3 = Column(String(100),)
    itog = Column(String(200),)

    vsego_dney = Column(Integer())
        #Дата
    date_begin = Column(DateTime(), )  # Дата начала основного и дополнительного отпуска
    date_end = Column(DateTime(), )  # Дата окончания основного и дополнительного отпуска

    date_create = Column(DateTime(), )
    date_edit = Column(DateTime(), )
    creator_id = Column(Integer(), )
    editor_id = Column(Integer(), )
    active = Column(Boolean, nullable=False)  # Активность записи

    def __init__(self,worker_id,period,osnov, kolvo_dney,dop_1,dop_2,dop_3, itog,vsego_dney,date_begin,date_end, date_create, date_edit, creator_id, editor_id, active):
        self.worker_id = worker_id

        self.period = period
        self.osnov = osnov
        self.kolvo_dney = kolvo_dney
        self.dop_1 = dop_1
        self.dop_2 = dop_2
        self.dop_3 = dop_3
        self.itog = itog
        self.vsego_dney = vsego_dney
        self.date_begin = date_begin
        self.date_end = date_end


        self.date_create = date_create
        self.date_edit = date_edit
        self.creator_id = creator_id
        self.editor_id = editor_id
        self.active = active

    def __repr__(self):
            return "<Vacation('%s','%s','%s', '%s', '%s', '%s', '%s', '%s', '%s'" \
                   ", '%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % \
                   (self.worker_id, self.period,self.osnov,self.kolvo_dney,self.dop_1 ,self.dop_2 ,
                    self.dop_3,self.itog,self.vsego_dney, self.date_begin,self.date_end,
                    self.date_create, self.date_edit, self.creator_id, self.editor_id,
                                                                        self.active)

def table_serializer(obj):
    return {
        'id': obj.id,
        'worker_id':obj.worker_id,

        'period': obj.period,
        'osnov': obj.osnov,
        'kolvo_dney': obj.kolvo_dney,
        'dop_1': obj.dop_1,
        'dop_2': obj.dop_2,
        'dop_3': obj.dop_3,
        'itog': obj.itog,
        'vsego_dney': obj.vsego_dney,
        'date_begin': obj.date_begin,
        'date_end': obj.date_end,

        'date_create':obj.date_create,
        'date_edit':obj.date_edit,
        'creator_id':obj.creator_id,
        'editor_id':obj.editor_id,
        'active':obj.active

    }



class VacationIndexEndpoint(Endpoint, GetListMixin, CreateMixin):

    name = 'list'
    many = True
    response_handler = DBResponseHandler


    def get_response_handler_params(self, **params):
        params['serializer'] = table_serializer
        return params

    def get_objects(self):

        table = session.query(Vacation).all()
        return table

    def save_object(self, obj):

        table = Vacation(**obj)
        Base.session.add(Vacation)
        session.commit()
        return table


class VacationObjectEndpoint(Endpoint, GetObjectMixin,
                              PutObjectMixin, DeleteObjectMixin):

    name = 'object'
    url = '/<string:obj_id>'
    response_handler = DBResponseHandler

    def get_response_handler_params(self, **params):

        params['serializer'] = table_serializer
        return params

    def get_object(self):

        obj_id = self.kwargs['obj_id']
        obj = session.query(Vacation).filter(Vacation.id == obj_id).one_or_none()
        if not obj:
            payload = {
                "message": "Users object not found.",
            }
            self.return_error(404, payload=payload)

        return obj

    def update_object(self, obj):

        data = self.request.data
        allowed_fields = ['worker_id','period','osnov', 'kolvo_dney','dop_1','dop_2','dop_3', 'itog','vsego_dney',
                          'date_begin','date_end', 'date_create', 'date_edit', 'creator_id', 'editor_id', 'active']

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