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



class Assignment_and_relocation(Base):
    __tablename__ = 'assignment_and_relocation'
            # Назначение и перемещение


    id = Column(Integer(), primary_key=True)
    worker_id = Column(Integer(), nullable=False)
    date = Column(DateTime(),)
    otdel = Column(String(100),)# Цех, отдел, участок
    prof = Column(String(100),)#Профессия, должность
    sootvetst = Column(String(100),)# Соответствие специальности по диплому(свидетельству) занимаемой должности(профессии) (да, нет)
    razrad = Column(String(100),unique=True,nullable=False)#тарифный разрад
    uslov_truda = Column(String(100))#Условия труда
                #Основание
    osnov_doc = Column(String(100))#наименование документа
    osnov_date = Column(DateTime(),)#дата
    nomer = Column(Integer())

    date_create = Column(DateTime(), )
    date_edit = Column(DateTime(), )
    creator_id = Column(Integer(), )
    editor_id = Column(Integer(), )
    active = Column(Boolean, nullable=False)  # Активность записи

    def __init__(self,date,otdel, prof, sootvetst , razrad, uslov_truda,
                 osnov_doc, osnov_date, nomer, date_create, date_edit, creator_id, editor_id, active):
        self.date = date
        self.otdel = otdel
        self.prof = prof
        self.sootvetst = sootvetst
        self.razrad = razrad
        self.uslov_truda = uslov_truda
        self.osnov_doc = osnov_doc
        self.osnov_date = osnov_date
        self.nomer = nomer
        self.date_create = date_create
        self.date_edit = date_edit
        self.creator_id = creator_id
        self.editor_id = editor_id
        self.active = active

    def __repr__(self):
            return "<Assignment_and_relocation('%s','%s', '%s', '%s', '%s', '%s', '%s','%s','%s','%s','%s','%s','%s','%s')>" % \
                   (self.date,self.otdel, self.prof, self.sootvetst , self.razrad,
                    self.uslov_truda, self.osnov_doc, self.osnov_date,self.nomer,
                    self.date_create, self.date_edit, self.creator_id, self.editor_id,
                                                                        self.active)

def table_serializer(obj):
    return {
        'id': obj.id,
        'date': obj.date,
        'otdel': obj.otdel,
        'prof': obj.prof,
        'sootvetst': obj.sootvetst,
        'razrad':obj.razrad,
        'uslov_truda':obj.uslov_truda,
        'osnov_doc':obj.osnov_doc,
        'osnov_date':obj.osnov_date,
        'nomer':obj.nomer,
        'date_create':obj.date_create,
        'date_edit':obj.date_edit,
        'creator_id':obj.creator_id,
        'editor_id':obj.editor_id,
        'active':obj.active

    }



class TableIndexEndpoint(Endpoint, GetListMixin, CreateMixin):

    name = 'list'
    many = True
    response_handler = DBResponseHandler


    def get_response_handler_params(self, **params):
        params['serializer'] = table_serializer
        return params

    def get_objects(self):

        table = session.query(Assignment_and_relocation).all()
        return table

    def save_object(self, obj):

        table = Assignment_and_relocation(**obj)
        Base.session.add(Assignment_and_relocation)
        session.commit()
        return table


class TableObjectEndpoint(Endpoint, GetObjectMixin,
                              PutObjectMixin, DeleteObjectMixin):

    name = 'object'
    url = '/<string:obj_id>'
    response_handler = DBResponseHandler

    def get_response_handler_params(self, **params):

        params['serializer'] = table_serializer
        return params

    def get_object(self):

        obj_id = self.kwargs['obj_id']
        obj = session.query(Assignment_and_relocation).filter(Assignment_and_relocation.id == obj_id).one_or_none()
        if not obj:
            payload = {
                "message": "Users object not found.",
            }
            self.return_error(404, payload=payload)

        return obj

    def update_object(self, obj):

        data = self.request.data
        allowed_fields = ['date','otdel', 'prof', 'sootvetst' , 'razrad', 'uslov_truda',
                 'osnov_doc', 'osnov_date', 'nomer', 'date_create', 'date_edit', 'creator_id', 'editor_id', 'active']

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