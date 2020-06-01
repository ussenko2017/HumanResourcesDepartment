from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy.orm import sessionmaker
from arrested import (
    ArrestedAPI, Resource, Endpoint, GetListMixin, CreateMixin,
    GetObjectMixin, PutObjectMixin, DeleteObjectMixin, ResponseHandler
)
from config import SQLALCHEMY_DB_URI

from config import DEBUG

engine = create_engine(SQLALCHEMY_DB_URI, echo=DEBUG)
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
        #  Личная карточка
    #  1.Общие сведения
    id = Column(Integer(), primary_key=True)
    lastname = Column(String(60),nullable=False)# 1 - Фамилия
    firstname = Column(String(60),nullable=False)# 1 - Имя
    patr = Column(String(60),)# 1 - Отчество
    gender_id = Column(Integer(), nullable=False)#пол id
    birthday = Column(String(50),)# 2 -дата рождения
    email = Column(String(50),unique=True  )#почта
    image_name = Column(String(100),)#название изображения  директории '/files/photo/worker'
    active = Column(Boolean,nullable=False)#Активность записи
    birthplace = Column(String(300),)# 3 - Место рождения
    nation = Column(String(100), )# 4 - Национальность
    education = Column(String(2000), )# 5 - Образование
    spec_diplom = Column(String(500), )# 6 - Специальность по диплому
    kvalif_diplom = Column(String(500),)# 7 - Квалификация по диплому
    academ_title = Column(String(500),)# 8 - Ученое звание
    profession = Column(String(500),)# 9 - Процессия: основная и др.
    position = Column(String(100),)# 10 - Должность
    stage_work = Column(String(100),)# 10- Стаж работы
    stage_main_position = Column(String(300),)#11 - По основной профессии, должности
    stage_all  = Column(String(100), )# 12- Общий
    stage_unbreak = Column(String(100), )# 13 - Непрерывный
    stage_self = Column(String(100), ) # 14 - В том числе на данном предприятии
    family_pos = Column(String(100), ) # 15 - Семейное положение
    family_comp = Column(String(500), ) # 16, 17, 18 Состав семьи
    issuedBy_series_dateIssue = Column(String(1000))# 19 - Кем выдан, Дата выдачи, Серия
    address = Column(String(300), )# 20 - Домашний адрес
    phone_number = Column(String(20), )  # 20 - номер телефона


        # 2. Сведения о воинском учете
    acc_group = Column(String(500))  # Группа учета
    acc_category = Column(String(500))  # Категория учета
    compos = Column(String(200), )# Cостав
    military_rank = Column(String(200),)# Воинское
    military_acc = Column(String(200), )# Военно-учетная
    suitability = Column(String(200), )# Годность к военной службе
    military_comm = Column(String(200),)#Название райвоенкомата по месту жительства
    special_acc = Column(String(200), )#Состоит на специальном воинском учете


    date_create = Column(DateTime(),)
    date_edit = Column(DateTime(),)
    creator_id = Column(Integer(),)
    editor_id = Column(Integer(),)
    """
    #   3. Назначение и перемещение
    assignment_and_relocation_id = Column(Integer(),)# id записи в таблице assignment_and_relocation
    #   4. Повышение квалификации
    kvalif_up_id = Column(Integer(), )  # id записи в таблице kvalif_up
    #   5. Переподготовка
    retraining_id = Column(Integer(), )  # id записи в таблице retraining
    #   6. Отпуска
    vacation_id = Column(Integer(), )# id записи в таблице vacation
    #   7. Аттестация
    vac_certification_id = Column(Integer(), )# id записи в таблице vac_certification
    8. Дополнительные сведения
    """


    info = Column(String(5000), )# Доп. сведения
    dismissal = Column(String(200), )# Дата и причина увольнения
    order = Column(String(200), )#Приказ



    

    def __init__(self, lastname, firstname , patr, gender_id, birthday,email, image_name, active,birthplace,
                 nation, education, spec_diplom, kvalif_diplom, academ_title, profession, position,
    stage_work, stage_main_position, stage_all, stage_unbreak, stage_self, family_pos, family_comp,
    issuedBy_series_dateIssue, address, phone_number, acc_group, acc_category, compos, military_rank,
    military_acc, suitability, military_comm, special_acc, info, dismissal, order,date_create,date_edit,creator_id,editor_id):

        self.lastname = lastname
        self.firstname = firstname
        self.patr = patr
        self.gender_id = gender_id
        self.birthday = birthday
        self.email = email
        self.image_name = image_name
        self.active = active
        self.birthplace = birthplace
        self.nation = nation
        self.education = education
        self.spec_diplom = spec_diplom
        self.kvalif_diplom = kvalif_diplom
        self.academ_title = academ_title
        self.profession = profession
        self.position = position
        self.stage_work = stage_work
        self.stage_main_position = stage_main_position
        self.stage_all = stage_all
        self.stage_unbreak = stage_unbreak
        self.stage_self = stage_self
        self.family_pos = family_pos
        self.family_comp = family_comp
        self.issuedBy_series_dateIssue = issuedBy_series_dateIssue
        self.address = address
        self.phone_number = phone_number
        self.acc_group = acc_group
        self.acc_category = acc_category
        self.compos = compos
        self.military_rank = military_rank
        self.military_acc = military_acc
        self.suitability = suitability
        self.military_comm = military_comm
        self.special_acc = special_acc
        self.info = info
        self.dismissal = dismissal
        self.order = order
        self.date_create = date_create
        self.date_edit = date_edit
        self.creator_id = creator_id
        self.editor_id = editor_id

    def __repr__(self):
            return "<Worker('%s','%s', '%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s', '%s'," \
                   " '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', " \
                   "'%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')>" \
                                                                    % (self.lastname,
                                                                        self.firstname, self.patr,self.gender_id,
                                                                        self.birthday, self.email, self.image_name, self.active,
                                                                                   self.birthplace,self.nation,self.education,
                                                                                   self.spec_diplom,self.kvalif_diplom,
                                                                                   self.academ_title,self.profession,
                                                                                   self.position,self.stage_work,
                                                                                   self.stage_main_position,self.stage_all,
                                                                                   self.stage_unbreak,self.stage_self,
                                                                                   self.family_pos,self.family_comp,
                                                                                   self.issuedBy_series_dateIssue,self.address,
                                                                                   self.phone_number,self.acc_group,
                                                                                   self.acc_category,self.compos,
                                                                                   self.military_rank,self.military_acc,
                                                                                   self.suitability,self.military_comm,
                                                                                   self.special_acc, self.info,
                                                                                   self.dismissal,self.order,self.date_create,
                                                                       self.date_edit,self.creator_id,self.editor_id)

def worker_serializer(obj):
    return {
        'id': obj.id,
        'lastname': obj.lastname,
        'firstname': obj.firstname,
        'patr': obj.patr,
        'gender_id': obj.gender_id,
        'birthday': obj.birthday,
        'email': obj.email,
        'image_name': obj.image_name,
        'active':obj.active,
        'birthplace':obj.birthplace,
        'nation':obj.nation,
        'education':obj.education,
        'spec_diplom':obj.spec_diplom,
        'kvalif_diplom':obj.kvalif_diplom,
        'academ_title':obj.academ_title,
        'profession':obj.profession,
        'position':obj.position,
        'stage_work':obj.stage_work,
        'stage_main_position':obj.stage_main_position,
        'stage_all':obj.stage_all,
        'stage_unbreak':obj.stage_unbreak,
        'stage_self':obj.stage_self,
        'family_pos':obj.family_pos,
        'family_comp':obj.family_comp,
        'issuedBy_series_dateIssue':obj.issuedBy_series_dateIssue,
        'address':obj.address,
        'phone_number':obj.phone_number,
        'acc_group':obj.acc_group,
        'acc_category':obj.acc_category,
        'compos':obj.compos,
        'military_rank':obj.military_rank,
        'military_acc':obj.military_acc,
        'suitability':obj.suitability,
        'military_comm':obj.military_comm,
        'special_acc':obj.special_acc,
        'info':obj.info,
        'dismissal':obj.dismissal,
        'order':obj.order,
        'date_create':obj.date_create,
        'date_edit' :obj.date_edit,
        'creator_id':obj.creator_id,
        'editor_id' :obj.editor_id

    }



class WorkerIndexEndpoint(Endpoint, GetListMixin, CreateMixin):

    name = 'list'
    many = True
    response_handler = DBResponseHandler


    def get_response_handler_params(self, **params):
        params['serializer'] = worker_serializer
        return params

    def get_objects(self):

        workers = session.query(Worker).all()
        return workers

    def save_object(self, obj):

        workers = Worker(**obj)
        Base.session.add(Worker)
        session.commit()
        return workers


class WorkerObjectEndpoint(Endpoint, GetObjectMixin,
                              PutObjectMixin, DeleteObjectMixin):

    name = 'object'
    url = '/<string:obj_id>'
    response_handler = DBResponseHandler

    def get_response_handler_params(self, **params):

        params['serializer'] = worker_serializer
        return params

    def get_object(self):

        obj_id = self.kwargs['obj_id']
        obj = session.query(Worker).filter(Worker.id == obj_id).one_or_none()
        if not obj:
            payload = {
                "message": "Worker object not found.",
            }
            self.return_error(404, payload=payload)

        return obj

    def update_object(self, obj):

        data = self.request.data
        allowed_fields = ['email','lastname','firstname','patr','birthday', 'active','image_name','gender_id','birthplace','nation',
                 'education','spec_diplom','kvalif_diplom','academ_title','profession','position','stage_work',
                      'stage_main_position','stage_all','stage_unbreak','stage_self','family_pos','family_comp',
                          'issuedBy_series_dateIssue','address','phone_number','acc_group','acc_category',
                          'compos','military_rank','military_acc','suitability','military_comm','special_acc',
                          'info','dismissal', 'order', 'date_create','date_edit','creator_id','editor_id'
                          ]

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
session.close()