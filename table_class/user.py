from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine, DateTime
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



class User(Base):
    __tablename__ = 'user'
    id = Column(Integer(), primary_key=True)
    lastname = Column(String(50),)
    firstname = Column(String(50),)
    patr = Column(String(50),)
    birthday = Column(String(50),)
    nickname = Column(String(50),)
    email = Column(String(50),unique=True )
    password = Column(String(50),)

    def __init__(self,nickname,email,password, lastname, firstname , patr, birthday):
        self.nickname = nickname
        self.email = email
        self.password = password
        self.lastname = lastname
        self.firstname = firstname
        self.patr = patr
        self.birthday  = birthday

    def __repr__(self):
            return "<User('%s','%s', '%s', '%s', '%s', '%s', '%s')>" % (self.nickname, self.email,
                                                                        self.password, self.lastname,
                                                                        self.firstname, self.patr,
                                                                        self.birthday)

def users_serializer(obj):
    return {
        'id': obj.id,
        'nickname': obj.nickname,
        'email': obj.email,
        'password': obj.password,
        'lastname': obj.lastname,
        'firstname':obj.firstname,
        'patr':obj.patr,
        'birthday':obj.birthday
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
        allowed_fields = ['nickname','email','password','lastname','firstname','patr','birthday']

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