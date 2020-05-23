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



class Staff_list(Base):
    __tablename__ = 'staff_list'
            # Штатное расписание

    #Структурное подразделение
    id = Column(Integer(), primary_key=True)
    name = Column(String(200), )  #наименование

    dolzh = Column(String(200), )  #должность

    kol_vo = Column(Integer(), nullable=False)#количество штатных единиц

    oklad = Column(Integer(), )#оклад, тарифная ставка(тенге)

    #Надбавка(тенге)
    nadbavka_1 = Column(Integer(), )#надбавка(тенге)
    nadbavka_2 = Column(Integer(), )#надбавка(тенге)
    nadbavka_3 = Column(Integer(), )#надбавка(тенге)

    fond = Column(Integer(), )#Месячный фонд(тенге)

    comment = Column(String(200), )  #Примечание



    date_create = Column(DateTime(), )
    date_edit = Column(DateTime(), )
    creator_id = Column(Integer(), )
    editor_id = Column(Integer(), )
    active = Column(Boolean, nullable=False)  # Активность записи

    def __init__(self,name,dolzh,kol_vo, oklad, nadbavka_1 , nadbavka_2, nadbavka_3,
                 fond, comment, date_create, date_edit, creator_id, editor_id, active):
        self.name = name
        self.dolzh = dolzh
        self.kol_vo = kol_vo
        self.oklad = oklad
        self.nadbavka_1 = nadbavka_1
        self.nadbavka_2 = nadbavka_2
        self.nadbavka_3 = nadbavka_3
        self.fond = fond
        self.comment = comment
        self.date_create = date_create
        self.date_edit = date_edit
        self.creator_id = creator_id
        self.editor_id = editor_id
        self.active = active

    def __repr__(self):
            return "<Staff_list('%s','%s','%s', '%s', '%s', '%s', '%s', '%s','%s','%s','%s','%s','%s','%s')>" % \
                   (self.name, self.dolzh,self.kol_vo, self.oklad, self.nadbavka_1 , self.nadbavka_2,
                    self.nadbavka_3, self.fond, self.comment,
                    self.date_create, self.date_edit, self.creator_id, self.editor_id,
                                                                        self.active)

def table_serializer(obj):
    return {
        'id': obj.id,
        'name':obj.name,
        'dolzh': obj.dolzh,
        'kol_vo': obj.kol_vo,
        'oklad': obj.oklad,
        'nadbavka_1': obj.nadbavka_1,
        'nadbavka_2':obj.nadbavka_2,
        'nadbavka_3':obj.nadbavka_3,
        'fond':obj.fond,
        'comment':obj.comment,
        'date_create':obj.date_create,
        'date_edit':obj.date_edit,
        'creator_id':obj.creator_id,
        'editor_id':obj.editor_id,
        'active':obj.active

    }



class Staff_listIndexEndpoint(Endpoint, GetListMixin, CreateMixin):

    name = 'list'
    many = True
    response_handler = DBResponseHandler


    def get_response_handler_params(self, **params):
        params['serializer'] = table_serializer
        return params

    def get_objects(self):

        table = session.query(Staff_list).all()
        return table

    def save_object(self, obj):

        table = Staff_list(**obj)
        Base.session.add(Staff_list)
        session.commit()
        return table


class Staff_listObjectEndpoint(Endpoint, GetObjectMixin,
                              PutObjectMixin, DeleteObjectMixin):

    name = 'object'
    url = '/<string:obj_id>'
    response_handler = DBResponseHandler

    def get_response_handler_params(self, **params):

        params['serializer'] = table_serializer
        return params

    def get_object(self):

        obj_id = self.kwargs['obj_id']
        obj = session.query(Staff_list).filter(Staff_list.id == obj_id).one_or_none()
        if not obj:
            payload = {
                "message": "Users object not found.",
            }
            self.return_error(404, payload=payload)

        return obj

    def update_object(self, obj):

        data = self.request.data
        allowed_fields = ['name','dolzh','kol_vo', 'oklad', 'nadbavka_1' , 'nadbavka_2', 'nadbavka_3',
                 'fond', 'comment', 'date_create', 'date_edit', 'creator_id', 'editor_id', 'active']

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