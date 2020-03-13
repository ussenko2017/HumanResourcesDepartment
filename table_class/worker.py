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



class Worker(Base):
    __tablename__ = 'worker'
    id = Column(Integer(), primary_key=True)
    lastname = Column(String(60),)# 1 - Фамилия
    firstname = Column(String(60),)# 1 - Имя
    patr = Column(String(60),)# 1 - Отчество
    gender_id = Column(Integer(), nullable=False)#пол id
    phone_number = Column(String(20),)#номер телефона
    birthday = Column(String(50),)# 2 -дата рождения
    nickname = Column(String(50),unique=True,nullable=False)#логин/ник
    email = Column(String(50),unique=True  )#почта
    password = Column(String(50),)#пароль
    image_name = Column(String(100),)#название изображения  директории '/files/photo/worker'
    active = Column(Boolean,nullable=False)#Активность записи
    birthplace = Column(String(300),)# 3 - Место рождения
    nation = Column(String(100), )# 4 - Национальность
    education = Column(String(2000), )# 5 - Образование
    spec_diplom = Column(String(500), )# 6 - Специальность по диплому3333333333333333333333
    kvalif_diplom = Column(String(500),)# 7 - Квалификация по диплому
    academ_title = Column(String(500))# 8 - Ученое звание
    profession = Column(String(500))# 9 - Процессия: основная и др.
    position = Column(String)



    acc_group = Column(String(500))  # Шруппа учета
    acc_category = Column(String(500))  # Категория учета
    def __init__(self,nickname,email,password, lastname, firstname , patr, birthday, active, image_name):
        self.nickname = nickname
        self.email = email
        self.password = password
        self.lastname = lastname
        self.firstname = firstname
        self.patr = patr
        self.birthday  = birthday
        self.active = active
        self.image_name = image_name

    def __repr__(self):
            return "<User('%s','%s', '%s', '%s', '%s', '%s', '%s','%s', '%s')>" % (self.nickname, self.email,
                                                                        self.password, self.lastname,
                                                                        self.firstname, self.patr,
                                                                        self.birthday, self.active, self.image_name)

def users_serializer(obj):
    return {
        'id': obj.id,
        'nickname': obj.nickname,
        'email': obj.email,
        'password': obj.password,
        'lastname': obj.lastname,
        'firstname':obj.firstname,
        'patr':obj.patr,
        'birthday':obj.birthday,
        'active':obj.active,
        'image_name':obj.image_name
    }



class UsersIndexEndpoint(Endpoint, GetListMixin, CreateMixin):

    name = 'list'
    many = True
    response_handler = DBResponseHandler


    def get_response_handler_params(self, **params):
        params['serializer'] = users_serializer
        return params

    def get_objects(self):

        otdels = session.query(User).all()
        return otdels

    def save_object(self, obj):

        users = User(**obj)
        Base.session.add(User)
        session.commit()
        return users


class UsersObjectEndpoint(Endpoint, GetObjectMixin,
                              PutObjectMixin, DeleteObjectMixin):

    name = 'object'
    url = '/<string:obj_id>'
    response_handler = DBResponseHandler

    def get_response_handler_params(self, **params):

        params['serializer'] = users_serializer
        return params

    def get_object(self):

        obj_id = self.kwargs['obj_id']
        obj = session.query(User).filter(User.id == obj_id).one_or_none()
        if not obj:
            payload = {
                "message": "Users object not found.",
            }
            self.return_error(404, payload=payload)

        return obj

    def update_object(self, obj):

        data = self.request.data
        allowed_fields = ['nickname','email','password','lastname','firstname','patr','birthday', 'active','image_name']

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