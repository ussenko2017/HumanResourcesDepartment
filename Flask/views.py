# -*- coding: utf-8 -*-

from datetime import datetime

import sqlalchemy
from flask import render_template, jsonify,request
from Flask import app
import json
import random
import requests
import Flask.mod
from table_class import user as clUser,worker as worker_py,kvalif_up as kvalif_up_py, retraining as retraining_py, vac_certification as vac_certification_py, vacation as vacation_py
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine, DateTime, inspect
import flask
import flask_login
from config import SQLALCHEMY_DB_URI, DEBUG
from flask import render_template, g
import logging
logging.basicConfig(level = logging.DEBUG)
logging.info("Hello views!")
logging.basicConfig(filename="log.txt", level = logging.INFO)


#uploads_block_begin
#from flask_uploads import UploadSet, configure_uploads, IMAGES,UploadNotAllowed
UPLOADED_PHOTOS_DEST_USER = '/files/photo/user'
UPLOADED_PHOTOS_DEST_WORKER = '/files/photo/worker'
app.config.from_object(__name__)
app.config.from_envvar('PHOTOLOG_SETTINGS', silent=True)
#uploaded_photos = UploadSet('photos', IMAGES)
#configure_uploads(app, uploaded_photos)
#uploads_block_end

#login_init
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

#engine, session init
engine = create_engine(SQLALCHEMY_DB_URI, echo=DEBUG)
Session = sessionmaker(bind=engine)



class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(nickname):
    session = Session()
    try:
        user_cl = session.query(clUser.User).filter_by(nickname=nickname).first()
    except:
        return
    user = User()
    user.id = user_cl.nickname
    user.num = user_cl.id
    user.firstname = user_cl.firstname
    user.lastname = user_cl.lastname
    user.patr = user_cl.patr
    user.birthday = user_cl.birthday
    user.nickname = user_cl.nickname
    user.password = user_cl.password
    user.email = user_cl.email
    user.active = user_cl.active



    return user


@login_manager.request_loader
def request_loader(request):
    session = Session()
    nickname = request.form.get('nickname')
    try:
        user_cl = session.query(clUser.User).filter_by(nickname=nickname).first()
        user = User()
        user.id = user_cl.nickname
        user.num = user_cl.id
        user.firstname = user_cl.firstname
        user.lastname = user_cl.lastname
        user.patr = user_cl.patr
        user.birthday = user_cl.birthday
        user.nickname = user_cl.nickname
        user.password = user_cl.password
        user.email = user_cl.email
        user.active = user_cl.active


        # DO NOT ever store passwords in plaintext and always compare password
        # hashes using constant-time comparison!
        user.is_authenticated = (flask.request.form['password'] == user_cl.password) and (user.active == 1)

        return user
    except:
        return




# users = {'foo@bar.tld': {'password': 'secret'}}



@app.route('/')
def home():
    main_header = 'Главная'
    session = Session()

    alert_html = request.args.get('alert_html')
    if alert_html is None:
        alert_html = ''

    try:
        user = flask_login.current_user.nickname

    except:
        user = 'Гость'
        return flask.redirect(flask.url_for('login_form'))

    return render_template('index.html',  user=user, alert_html=alert_html, main_header=main_header)


@app.route('/login_form', methods=['GET', 'POST'])
def login_form():
    try:
        user = flask_login.current_user.nickname
    except:
        return render_template('login_form.html')
    return flask.redirect(flask.url_for('home'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    session = Session()
    nickname = flask.request.form['nickname']
    print('Login: ' + nickname)
    try:

        user_cl = session.query(clUser.User).filter_by(nickname=nickname).first()
        print('Pass_base: ' + user_cl.password)
    except:
        return flask.redirect(flask.url_for('login_form'))

    print('Pass_post: ' + flask.request.form['password'])
    if flask.request.form['password'] == user_cl.password:
        user = User()
        user.id = user_cl.nickname
        user.num = user_cl.id
        user.firstname = user_cl.firstname
        user.lastname = user_cl.lastname
        user.patr = user_cl.patr
        user.birthday = user_cl.birthday
        user.nickname = user_cl.nickname
        user.password = user_cl.password
        user.email = user_cl.email
        user.active = user_cl.active


        flask_login.login_user(user)

    return flask.redirect(flask.url_for('home'))


@app.route('/profile')
@flask_login.login_required
def profile():
    return render_template('profile.html',user=flask_login.current_user)


@app.route('/logout')
def logout():
    flask_login.logout_user()
    g.user = 'Гость'
    return flask.redirect(flask.url_for('login_form'))


@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'





@app.route('/del', methods=['GET', 'POST'])
def delete():
    session = Session()
    id = flask.request.values['id']
    redirect = flask.request.values['redirect']
    tablename = flask.request.values['tablename']
    sql = "DELETE FROM `" + tablename + "` WHERE `" + tablename+"`.id = " + id
    session.execute(sql)
    session.commit()
    return flask.redirect(flask.url_for(redirect))

@app.route('/user', methods=['GET', 'POST'])
def user():
    alert_html = request.args.get('alert_html')
    if alert_html is None:
        alert_html = ''

    main_header = 'Администрирование'
    session = Session()
    users = session.query(clUser.User).all()
    return render_template('tables/user.html', users=users, main_header=main_header, alert_html=alert_html)

@app.route('/user-add', methods=['GET', 'POST'])
def user_add():
    main_header = 'Администрирование'
    header_text = ' Добавление учетной записи'

    return render_template('add_edit_table/user.html', header_text=header_text, main_header=main_header, type_str='add')

@app.route('/user-edit', methods=['GET', 'POST'])
def user_edit():
    main_header = 'Администрирование'
    header_text = ' Редактирование учетной записи'
    session = Session()
    id = flask.request.values['id']
    user_cl = session.query(clUser.User).filter_by(id=id).first()



    return render_template('add_edit_table/user.html', user_cl=user_cl, header_text=header_text, main_header=main_header, type_str='edit')

@app.route('/user-save', methods=['GET', 'POST'])
def user_save():
    active = None
    session = Session()
    try:
        if flask.request.values['active'] == 'on':
            active = True
    except:
        active = False
    if flask.request.values['id'] == 'add':
        user_cl = clUser.User(lastname=flask.request.values['lastname'],
                              firstname=flask.request.values['firstname'],
                              patr=flask.request.values['patr'],
                              birthday=flask.request.values['birthday'],
                              nickname=flask.request.values['nickname'],
                              email=flask.request.values['email'],
                              password=flask.request.values['password'],
                              active=active)

    else:
        id = flask.request.values['id']
        user_cl = session.query(clUser.User).filter_by(id=id).first()
        user_cl.lastname = flask.request.values['lastname']
        user_cl.firstname = flask.request.values['firstname']
        user_cl.patr = flask.request.values['patr']
        user_cl.birthday = flask.request.values['birthday']
        user_cl.nickname = flask.request.values['nickname']
        user_cl.email = flask.request.values['email']
        user_cl.password = flask.request.values['password']
        user_cl.active = active

    session.add(user_cl)
    try:
        session.commit()
        alert_html = Flask.mod.show_alert('success', 'Отлично! ', 'Пользовательские данные сохранены')
    except:
        alert_html = Flask.mod.show_alert('danger', 'Ошибка ', 'Пользовательские данные не были сохранены')


    users = session.query(clUser.User).all()

    return flask.redirect(flask.url_for('user', alert_html=alert_html))




@app.route('/worker', methods=['GET', 'POST'])
def worker():
    alert_html = request.args.get('alert_html')
    if alert_html is None:
        alert_html = ''

    main_header = 'Карточки работников'
    session = Session()
    workers = session.query(worker_py.Worker).all()
    return render_template('tables/worker.html', workers=workers, main_header=main_header, alert_html=alert_html)



@app.route('/worker-add', methods=['GET', 'POST'])
def worker_add():
    main_header = 'Карточки работников'
    header_text = ' Создание новой карточки'

    return render_template('add_edit_table/worker.html', header_text=header_text, main_header=main_header, type_str='add')



@app.route('/worker-edit', methods=['GET', 'POST'])
def worker_edit():
    alert_html = request.args.get('alert_html')
    if alert_html is None:
        alert_html = ''
    main_header = 'Карточки работников'
    header_text = ' Редактирование карточки'
    session = Session()
    id = flask.request.values['id']
    wor = session.query(worker_py.Worker).filter_by(id=id).first()



    return render_template('add_edit_table/worker.html', worker=wor, header_text=header_text, main_header=main_header, type_str='edit',alert_html=alert_html)


@app.route('/worker-card-add', methods=['GET', 'POST'])
def worker_card_add():
    main_header = 'Карточки работников'
    header_text = ' Создание новой карточки'

    return render_template('add_edit_table/worker-card.html', header_text=header_text, main_header=main_header, type_str='add')

@app.route('/worker-card-edit', methods=['GET', 'POST'])
def worker_card_edit():
    main_header = 'Карточки работников'
    header_text = ' Редактирование карточки'
    session = Session()
    id = flask.request.values['id']
    wor = session.query(worker_py.Worker).filter_by(id=id).first()

    return render_template('add_edit_table/worker-card.html', worker=wor, header_text=header_text, main_header=main_header,
                           type_str='edit')

@app.route('/worker-list-add', methods=['GET', 'POST'])
def worker_list_add():
    main_header = 'Карточки работников'
    header_text = ' Создание новой карточки'

    return render_template('add_edit_table/worker-list.html', header_text=header_text, main_header=main_header, type_str='add')


@app.route('/worker-list-edit', methods=['GET', 'POST'])
def worker_list_edit():
    main_header = 'Карточки работников'
    header_text = ' Редактирование карточки'
    session = Session()
    id = flask.request.values['id']
    wor = session.query(worker_py.Worker).filter_by(id=id).first()

    return render_template('add_edit_table/worker-list.html', worker=wor, header_text=header_text, main_header=main_header,
                           type_str='edit')

@app.route('/worker-save', methods=['GET', 'POST'])
def worker_save():
    alert_html = Flask.mod.show_alert('success', 'Отлично! ', ' Данные работника сохранены')
    active = None
    session = Session()
    try:
        if flask.request.values['active'] == 'on':
            active = True
    except:
        active = False

    wor = ''
    try:    # Общие сведения
            logging.debug('Общие сведения - начало')
            lastname = flask.request.values['lastname']
            firstname = flask.request.values['firstname']
            patr = flask.request.values['patr']
            gender_id = flask.request.values['gender_id']
            birthday = flask.request.values['birthday']
            email = flask.request.values['email']
            creator_id = flask_login.current_user.num
            date_create = datetime.now()

            editor_id = creator_id
            date_edit = date_create
            logging.debug('Общие сведения - перед if')
            if flask.request.values['id'] == 'add':
                # Создание новой карточки посредством заполнения общих сведений
                logging.debug('Общие сведения - iF add - начало')
                wor = worker_py.Worker(lastname=lastname,firstname=firstname,patr=patr,gender_id=gender_id,
                                       birthday=birthday,email=email, creator_id=creator_id,date_create=date_create,
                                       date_edit=date_edit,editor_id=editor_id, active=active,
                image_name=None,
                birthplace=None,
                nation =None,
                education=None,
                spec_diplom =None,
                kvalif_diplom =None,
                academ_title=None,
                profession=None,
                position=None,
                stage_work=None,
                stage_main_position =None,
                stage_all =None,
                stage_unbreak =None,
                stage_self =None,
                family_pos =None,
                family_comp=None,
                issuedBy_series_dateIssue=None,
                address=None,
                phone_number=None,
                acc_group=None,
                acc_category=None,
                compos=None,
                military_rank=None,
                military_acc =None,
                suitability =None,
                military_comm=None,
                special_acc=None,
                info=None,
                dismissal=None,
                order=None)

                logging.debug('Общие сведения - iF - коммит')
                session.add(wor)
                session.commit()
                logging.debug('Общие сведения - iF - конец')

            else:
                # Редактирование карточки посредством перезаписи общих сведений
                logging.debug('Общие сведения - iF edit - начало')
                id = flask.request.values['id']
                wor = session.query(worker_py.Worker).filter_by(id=id).first()
                wor.lastname = flask.request.values['lastname']
                wor.firstname = flask.request.values['firstname']
                wor.patr = flask.request.values['patr']
                wor.gender_id = flask.request.values['gender_id']  # пол id
                wor.birthday = flask.request.values['birthday']
                wor.email = flask.request.values['email']
                wor.active = active
                # wor.date_create =
                wor.date_edit = datetime.now()
                # wor.creator_id =
                wor.editor_id = flask_login.current_user.num
                logging.debug('Общие сведения - iF edit - коммит, Editor:' + str(wor.editor_id))
                session.add(wor)
                session.commit()
                logging.debug('Общие сведения - iF edit - конец')


    except Exception as e:

        logging.error(str(e))
        try:
            # Личная карточка
            logging.debug('Личная карточка - начало')
            if flask.request.values['id'] == 'add':
                logging.debug('Личная карточка - IF add')
                pass
            else:
                # Редактирование Личной карточки
                logging.debug('Личная карточка - IF edit - начало')
                id = flask.request.values['id']
                wor = session.query(worker_py.Worker).filter_by(id=id).first()
                wor.image_name = flask.request.values['image_name']  # название изображения  директории '/files/photo/worker'

                wor.birthplace = flask.request.values['birthplace']  # 3 - Место рождения
                wor.nation = flask.request.values['nation']  # 4 - Национальность
                wor.education = flask.request.values['education']  # 5 - Образование
                wor.spec_diplom = flask.request.values['spec_diplom']  # 6 - Специальность по диплому
                wor.kvalif_diplom = flask.request.values['kvalif_diplom']  # 7 - Квалификация по диплому
                wor.academ_title = flask.request.values['academ_title']  # 8 - Ученое звание
                wor.profession = flask.request.values['profession']  # 9 - Процессия: основная и др.
                wor.position = flask.request.values['position']  # 10 - Должность
                wor.stage_work = flask.request.values['stage_work']  # 10- Стаж работы
                wor.stage_main_position = flask.request.values[
                    'stage_main_position']  # 11 - По основной профессии, должности
                wor.stage_all = flask.request.values['stage_all']  # 12- Общий
                wor.stage_unbreak = flask.request.values['stage_unbreak']  # 13 - Непрерывный
                wor.stage_self = flask.request.values['stage_self']  # 14 - В том числе на данном предприятии
                wor.family_pos = flask.request.values['family_pos']  # 15 - Семейное положение
                wor.family_comp = flask.request.values['family_comp']  # 16, 17, 18 Состав семьи
                wor.issuedBy_series_dateIssue = flask.request.values[
                    'issuedBy_series_dateIssue']  # 19 - Кем выдан, Дата выдачи, Серия
                wor.address = flask.request.values['address']  # 20 - Домашний адрес
                wor.phone_number = flask.request.values['phone_number']  # 20 - номер телефона

                # 2. Сведения о воинском учете
                wor.acc_group = flask.request.values['acc_group']  # Группа учета
                wor.acc_category = flask.request.values['acc_category']  # Категория учета
                wor.compos = flask.request.values['compos']  # Cостав
                wor.military_rank = flask.request.values['military_rank']  # Воинское
                wor.military_acc = flask.request.values['military_acc']  # Военно-учетная
                wor.suitability = flask.request.values['suitability']  # Годность к военной службе
                wor.military_comm = flask.request.values['military_comm']  # Название райвоенкомата по месту жительства
                wor.special_acc = flask.request.values['special_acc']  # Состоит на специальном воинском учете

                # wor.date_create =
                wor.date_edit = datetime.now()
                # wor.creator_id = Column(Integer(), )
                wor.editor_id = flask.request.values['creator_id']

                wor.info = flask.request.values['info']  # Доп. сведения
                wor.dismissal = flask.request.values['dismissal']  # Дата и причина увольнения
                wor.order = flask.request.values['order']  # Приказ
                logging.debug('Личная карточка - IF edit - коммит')
                session.add(wor)
                session.commit()
                logging.debug('Личная карточка - IF edit - конец')
        except Exception as e:
            logging.error(str(e))
            alert_html = Flask.mod.show_alert('error', 'Ошибка! ', ' Данные не были добавлены из-за ошибки: '+ str(e))
            #Личный лист


        #

    return flask.redirect(flask.url_for('worker', alert_html=alert_html))






@app.route('/vac-certification', methods=['GET', 'POST'])
def vac_certification():
    alert_html = request.args.get('alert_html')
    if alert_html is None:
        alert_html = ''

    main_header = 'Справочник "Аттестации"'
    session = Session()
    vac_cert = session.query(vac_certification.Vac_certification).all()
    return render_template('tables/vac_certification.html', vac_cert=vac_cert, main_header=main_header, alert_html=alert_html)

@app.route('/vac-certification-add', methods=['GET', 'POST'])
def vac_certification_add():
    main_header = 'Справочник "Аттестации"'
    header_text = ' Добавление "Аттестаций"'

    return render_template('add_edit_table/vac_certification.html', header_text=header_text, main_header=main_header, type_str='add')

@app.route('/vac-certification-edit', methods=['GET', 'POST'])
def vac_certification_edit():
    main_header = 'Справочник "Аттестации"'
    header_text = ' Редактирование "Аттестаций"'
    session = Session()
    id = flask.request.values['id']
    vac_cert = session.query(vac_certification.Vac_certification).filter_by(id=id).first()



    return render_template('add_edit_table/vac_certification.html', vac_cert=vac_cert, header_text=header_text, main_header=main_header, type_str='edit')

@app.route('/vac-certification-save', methods=['GET', 'POST'])
def vac_certification_save():
    active = None
    session = Session()
    try:
        if flask.request.values['active'] == 'on':
            active = True
    except:
        active = False
    if flask.request.values['id'] == 'add':
        user_cl = clUser.User(lastname=flask.request.values['lastname'],
                              firstname=flask.request.values['firstname'],
                              patr=flask.request.values['patr'],
                              birthday=flask.request.values['birthday'],
                              nickname=flask.request.values['nickname'],
                              email=flask.request.values['email'],
                              password=flask.request.values['password'],
                              active=active)

    else:
        id = flask.request.values['id']
        user_cl = session.query(clUser.User).filter_by(id=id).first()
        user_cl.lastname = flask.request.values['lastname']
        user_cl.firstname = flask.request.values['firstname']
        user_cl.patr = flask.request.values['patr']
        user_cl.birthday = flask.request.values['birthday']
        user_cl.nickname = flask.request.values['nickname']
        user_cl.email = flask.request.values['email']
        user_cl.password = flask.request.values['password']
        user_cl.active = active

    session.add(user_cl)
    session.commit()

    users = session.query(clUser.User).all()
    alert_html = Flask.mod.show_alert('success', 'Отлично! ', 'Пользовательские данные сохранены')
    return flask.redirect(flask.url_for('vac_certification', alert_html=alert_html))