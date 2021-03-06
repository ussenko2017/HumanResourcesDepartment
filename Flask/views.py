# -*- coding: utf-8 -*-
import os
from datetime import datetime

import mysql
import sqlalchemy
from flask import render_template, jsonify, request, send_from_directory
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

from Flask import app
import json
import random
import requests
import Flask.mod
from table_class import user as clUser,worker as worker_py,kvalif_up as kvalif_up_py, retraining as retraining_py, \
    vac_certification as vac_certification_py, vacation as vacation_py, \
    assignment_and_relocation as assignment_and_relocation_py, staff_list as staff_list_py, notes as notes_py
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine, DateTime, inspect
import flask
import flask_login
from config import SQLALCHEMY_DB_URI, DEBUG
from flask import render_template, g
import logging

workerlists_dir = "static/files/workerlists/"
personalList_dir = "static/files/personalLists/"
staffList_dir = "static/files/staffLists/"
UPLOADED_PHOTOS_DEST_USER = 'Flask/static/files/photo/user/'
UPLOADED_PHOTOS_DEST_WORKER = 'Flask/static/files/photo/worker/'
app.config['UPLOAD_FOLDER'] = UPLOADED_PHOTOS_DEST_USER

logging.basicConfig(filename="log.txt", level = logging.DEBUG)
logging.info("Hello views!")
app.config['img_count'] = 0

app.config.from_object(__name__)


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

    session.close()

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
        session.close()

        return user
    except:
        session.close()

        return




# users = {'foo@bar.tld': {'password': 'secret'}}



@app.route('/')
def home():
    main_header = 'Главная'
    session = Session()
    today = datetime.today()
    today = today.strftime("%Y-%m-%d")
    workers_count = session.execute('select count(id) from worker').first()[0]
    sql = "SELECT count(worker_id) FROM vacation inner join worker on worker.id = vacation.worker_id where "+"'"+today+"'"+  " between vacation.date_begin and vacation.date_end"
    vac_count = session.execute(sql).first()[0]
    proc_vac = (vac_count / workers_count) * 100
    proc_workers = 100 - proc_vac
    proc_vac = round(proc_vac, 1)
    proc_workers = round(proc_workers, 1)
    logging.error("Vac_count: " + str(vac_count))
    logging.error("Vac_sql: " + sql)
    alert_html = request.args.get('alert_html')
    if alert_html is None:
        alert_html = ''

    try:
        user = flask_login.current_user.nickname

    except:
        user = 'Гость'
        return flask.redirect(flask.url_for('login_form'))
    try:
        w = Flask.mod.getWeather()
    except:
        w = None

    import locale
    locale.setlocale(locale.LC_ALL, "")

    now = datetime.now()
    today = now.strftime("%A, %d. %B %Y %I:%M%p")
    time_now = now.strftime("%I:%M%p")

    arr_notes = []
    notes = session.execute('select * from notes inner join `user` on notes.creator_id = `user`.id')
    for n in notes:
        arr_notes.append(n)

    arr_notes.reverse()

    session.close()

    return render_template('index.html',w = w,notes = arr_notes,vac_count =vac_count, workers_count=workers_count,
                            proc_vac=proc_vac, proc_workers=proc_workers,
                           today=today,time_now=time_now, user=user, alert_html=alert_html, main_header=main_header, img_count=app.config['img_count'])


@app.route('/login_form', methods=['GET', 'POST'])
def login_form():
    try:
        user = flask_login.current_user.nickname
    except:
        return render_template('login_form.html')

    return flask.redirect(flask.url_for('home', img_count=app.config['img_count']))



@app.route('/login', methods=['GET', 'POST'])
def login():
    session = Session()
    nickname = flask.request.form['nickname']
    print('Login: ' + nickname)
    try:

        user_cl = session.query(clUser.User).filter_by(nickname=nickname).first()
        print('Pass_base: ' + user_cl.password)
    except:
        return flask.redirect(flask.url_for('login_form', img_count=app.config['img_count']))

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
    session.close()

    return flask.redirect(flask.url_for('home', img_count=app.config['img_count']))


@app.route('/profile')
@flask_login.login_required
def profile():
    return render_template('profile.html',user=flask_login.current_user, img_count=app.config['img_count'])


@app.route('/logout')
def logout():
    flask_login.logout_user()
    g.user = 'Гость'
    return flask.redirect(flask.url_for('login_form', img_count=app.config['img_count']))


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
    try:
            worker_id = flask.request.values['worker_id']
            wor = session.query(worker_py.Worker).filter_by(id=worker_id).first()
            session.close()
            return flask.redirect(flask.url_for(redirect,worker=wor, worker_id = worker_id, img_count=app.config['img_count']))
    except Exception as e:
        logging.error(str(e))
        return flask.redirect(flask.url_for(redirect, img_count=app.config['img_count']))








@app.route('/user', methods=['GET', 'POST'])
def user():
    alert_html = request.args.get('alert_html')
    if alert_html is None:
        alert_html = ''

    main_header = 'Администрирование системных пользователей'
    session = Session()
    users = session.query(clUser.User).all()
    return render_template('tables/user.html', users=users, main_header=main_header, alert_html=alert_html, img_count=app.config['img_count'])

@app.route('/user-add', methods=['GET', 'POST'])
def user_add():
    main_header = 'Администрирование системных пользователей'
    header_text = ' Добавление учетной записи'

    return render_template('add_edit_table/user.html', header_text=header_text, main_header=main_header, type_str='add', img_count=app.config['img_count'])

@app.route('/user-edit', methods=['GET', 'POST'])
def user_edit():
    main_header = 'Администрирование системных пользователей'
    header_text = ' Редактирование учетной записи'
    session = Session()
    id = flask.request.values['id']
    user_cl = session.query(clUser.User).filter_by(id=id).first()
    path = app.config['UPLOAD_FOLDER'] + str(id)+".png"
    img = False
    try:
        f = open(path)
        f.close()
        img = True
    except FileNotFoundError:
        path = "http://www.placehold.it/200x150/EFEFEF/AAAAAA&text=no+image"
    session.close()


    return render_template('add_edit_table/user.html', img = img, path = path, user_cl=user_cl, header_text=header_text, main_header=main_header, type_str='edit', img_count=app.config['img_count'])

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
    except Exception as e:
        logging.error(e)
        alert_html = Flask.mod.show_alert('danger', 'Ошибка ', 'Пользовательские данные не были сохранены')


    users = session.query(clUser.User).all()
    session.close()

    return flask.redirect(flask.url_for('user', alert_html=alert_html, img_count=app.config['img_count']))




@app.route('/worker', methods=['GET', 'POST'])
def worker():
    alert_html = request.args.get('alert_html')
    if alert_html is None:
        alert_html = ''

    main_header = 'Карточки работников'
    session = Session()
    workers = session.query(worker_py.Worker).all()
    session.close()

    return render_template('tables/worker.html', workers=workers, main_header=main_header, alert_html=alert_html, img_count=app.config['img_count'])



@app.route('/worker-add', methods=['GET', 'POST'])
def worker_add():
    main_header = 'Создание новой карточки работника'


    return render_template('add_edit_table/worker.html', main_header=main_header, type_str='add', img_count=app.config['img_count'])



@app.route('/worker-edit', methods=['GET', 'POST'])
def worker_edit():
    alert_html = request.args.get('alert_html')
    if alert_html is None:
        alert_html = ''
    main_header = 'Редактирование карточки работника'

    session = Session()
    id = flask.request.values['id']
    wor = session.query(worker_py.Worker).filter_by(id=id).first()
    wor.creator = session.query(clUser.User).filter_by(id=wor.creator_id).first()
    wor.editor = session.query(clUser.User).filter_by(id=wor.editor_id).first()
    session.close()

    return render_template('add_edit_table/worker.html', worker=wor, main_header=main_header, type_str='edit',alert_html=alert_html, img_count=app.config['img_count'])


@app.route('/worker-card-add', methods=['GET', 'POST'])
def worker_card_add():
    main_header = 'Создание новой карточки работника'


    return render_template('add_edit_table/worker-card.html', main_header=main_header, type_str='add', img_count=app.config['img_count'])

@app.route('/worker-card-edit', methods=['GET', 'POST'])
def worker_card_edit():
    main_header = 'Редактирование карточки работника'

    session = Session()
    id = flask.request.values['id']
    wor = session.query(worker_py.Worker).filter_by(id=id).first()
    wor.creator = session.query(clUser.User).filter_by(id=wor.creator_id).first()
    wor.editor = session.query(clUser.User).filter_by(id=wor.editor_id).first()
    session.close()

    return render_template('add_edit_table/worker-card.html', worker=wor,  main_header=main_header,
                           type_str='edit', img_count=app.config['img_count'])

@app.route('/worker-list-add', methods=['GET', 'POST'])
def worker_list_add():
    main_header = 'Создание новой карточки работника'


    return render_template('add_edit_table/worker-list.html',  main_header=main_header, type_str='add', img_count=app.config['img_count'])


@app.route('/worker-list-edit', methods=['GET', 'POST'])
def worker_list_edit():
    main_header = 'Редактирование карточки работника'

    session = Session()
    id = flask.request.values['id']
    wor = session.query(worker_py.Worker).filter_by(id=id).first()
    session.close()

    return render_template('add_edit_table/worker-list.html', worker=wor,  main_header=main_header,
                           type_str='edit', img_count=app.config['img_count'])

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
            empty = ''
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
                image_name=empty,
                birthplace=empty,
                nation =empty,
                education=empty,
                spec_diplom =empty,
                kvalif_diplom =empty,
                academ_title=empty,
                profession=empty,
                position=empty,
                stage_work=empty,
                stage_main_position =empty,
                stage_all =empty,
                stage_unbreak =empty,
                stage_self =empty,
                family_pos =empty,
                family_comp=empty,
                issuedBy_series_dateIssue=empty,
                address=empty,
                phone_number=empty,
                acc_group=empty,
                acc_category=empty,
                compos=empty,
                military_rank=empty,
                military_acc =empty,
                suitability =empty,
                military_comm=empty,
                special_acc=empty,
                info=empty,
                dismissal=empty,
                order=empty)

                logging.debug('Общие сведения - iF - коммит')
                try:
                    session.add(wor)
                    session.commit()
                except SQLAlchemyError as e:
                    alert_html = Flask.mod.show_alert('danger', 'Ошибка! ',
                                                      ' Данные не были добавлены. Указанный email уже есть в системе.')
                except Exception as e:
                    alert_html = Flask.mod.show_alert('danger', 'Ошибка! ',
                                                      ' Данные не были добавлены из-за ошибки: ' + str(e))

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
                wor.stage_main_position = flask.request.values['stage_main_position']  # 11 - По основной профессии, должности
                wor.stage_all = flask.request.values['stage_all']  # 12- Общий
                wor.stage_unbreak = flask.request.values['stage_unbreak']  # 13 - Непрерывный
                wor.stage_self = flask.request.values['stage_self']  # 14 - В том числе на данном предприятии
                wor.family_pos = flask.request.values['family_pos']  # 15 - Семейное положение
                wor.family_comp = flask.request.values['family_comp']  # 16, 17, 18 Состав семьи
                wor.issuedBy_series_dateIssue = flask.request.values['issuedBy_series_dateIssue']  # 19 - Кем выдан, Дата выдачи, Серия
                wor.address = flask.request.values['address']  # 20 - Домашний адрес
                wor.phone_number = flask.request.values['phone_number']  # 20 - номер телефона
                logging.debug('Личная карточка - IF edit - перед воинскими данными')
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
                wor.editor_id = flask_login.current_user.num

                wor.info = flask.request.values['info']  # Доп. сведения
                wor.dismissal = flask.request.values['dismissal']  # Дата и причина увольнения
                wor.order = flask.request.values['order']  # Приказ
                logging.debug('Личная карточка - IF edit - коммит')
                session.add(wor)
                session.commit()
                logging.debug('Личная карточка - IF edit - конец')
        except Exception as e:
            logging.error(str(e))
            alert_html = Flask.mod.show_alert('danger', 'Ошибка! ', ' Данные не были добавлены из-за ошибки: '+ str(e))
            #Личный лист


        #
    session.close()

    return flask.redirect(flask.url_for('worker', alert_html=alert_html, img_count=app.config['img_count']))






@app.route('/vac-certification', methods=['GET', 'POST'])
def vac_certification():
    alert_html = request.args.get('alert_html')
    worker_id = request.args.get('worker_id')
    if alert_html is None:
        alert_html = ''

    main_header = 'Аттестации'
    session = Session()
    vacs = []
    vac_cert = session.query(vac_certification_py.Vac_certification).filter_by(worker_id=worker_id).all()
    for ar in vac_cert:
        ar.creator = session.query(clUser.User).filter_by(id=ar.creator_id).first()
        ar.editor = session.query(clUser.User).filter_by(id=ar.editor_id).first()
        vacs.append(ar)
    wor = session.query(worker_py.Worker).filter_by(id=worker_id).first()

    session.close()

    return render_template('add_edit_table/vac_certification.html', vac_cert=vacs,worker=wor ,main_header=main_header, alert_html=alert_html, img_count=app.config['img_count'])



@app.route('/vac-certification-save', methods=['GET', 'POST'])
def vac_certification_save():
    alert_html = Flask.mod.show_alert('success', 'Отлично! ', ' Данные сохранены')
    active = None
    session = Session()
    try:
        if flask.request.values['active'] == 'on':
            active = True
    except:
        active = False
    creator_id = flask_login.current_user.num
    date_create = datetime.now()
    editor_id = creator_id
    date_edit = date_create
    worker_id = flask.request.values['worker_id']

    if flask.request.values['id'] == 'add':
        vac_cert = vac_certification_py.Vac_certification(worker_id=worker_id,
                              date=flask.request.values['date'],
                              result_com=flask.request.values['result_com'],
                              creator_id=creator_id,
                              date_create=date_create,
                              date_edit=date_edit,
                              editor_id=editor_id,
                              active=active)

    else:
        id = flask.request.values['id']
        vac_cert = session.query(vac_certification_py.Vac_certification).filter_by(id=id).first()

        vac_cert.worker_id = worker_id
        vac_cert.date = flask.request.values['date']
        vac_cert.result_com = flask.request.values['result_com']  # Решение комиссии
        vac_cert.active = active

        vac_cert.date_edit = date_edit
        vac_cert.editor_id = editor_id

    try:
        session.add(vac_cert)
        session.commit()
    except Exception as e:
        logging.error(str(e))
        alert_html = Flask.mod.show_alert('danger', 'Ошибка! ', ' Не удалось обработать запрос с ошибкой: ' + str(e))

    users = session.query(clUser.User).all()
    session.close()

    return flask.redirect(flask.url_for('vac_certification', alert_html=alert_html, worker_id=worker_id, img_count=app.config['img_count']))




@app.route('/assignment-and-relocation', methods=['GET', 'POST'])
def assignment_and_relocation():
    alert_html = request.args.get('alert_html')
    worker_id = request.args.get('worker_id')
    if alert_html is None:
        alert_html = ''

    main_header = 'Назначение и перемещение'
    session = Session()
    ars = []
    as_reloc = session.query(assignment_and_relocation_py.Assignment_and_relocation).filter_by(worker_id=worker_id).all()
    for ar in as_reloc:
        ar.creator = session.query(clUser.User).filter_by(id=ar.creator_id).first()
        ar.editor = session.query(clUser.User).filter_by(id=ar.editor_id).first()
        ars.append(ar)
    wor = session.query(worker_py.Worker).filter_by(id=worker_id).first()
    session.close()

    return render_template('add_edit_table/assignment_and_relocation.html', as_reloc=ars,worker=wor ,main_header=main_header, alert_html=alert_html, img_count=app.config['img_count'])



@app.route('/assignment-and-relocation-save', methods=['GET', 'POST'])
def assignment_and_relocation_save():
    alert_html = Flask.mod.show_alert('success', 'Отлично! ', ' Данные сохранены')
    active = None
    session = Session()
    try:
        if flask.request.values['active'] == 'on':
            active = True
    except:
        active = False
    creator_id = flask_login.current_user.num
    date_create = datetime.now()
    editor_id = creator_id
    date_edit = date_create
    worker_id = flask.request.values['worker_id']

    if flask.request.values['id'] == 'add':
        as_reloc = assignment_and_relocation_py.Assignment_and_relocation(worker_id=worker_id,
                              date=flask.request.values['date'],
                              otdel = flask.request.values['otdel'] ,
                              prof = flask.request.values['prof'] ,
                              sootvetst = flask.request.values['sootvetst'],
                              razrad = flask.request.values['razrad'] ,
                              uslov_truda = flask.request.values['uslov_truda'],
                              osnov_doc = flask.request.values['osnov_doc'] ,
                              osnov_date = flask.request.values['osnov_date'] ,
                              nomer = flask.request.values['nomer'],
                              creator_id=creator_id,
                              date_create=date_create,
                              date_edit=date_edit,
                              editor_id=editor_id,
                              active=active)

    else:
        id = flask.request.values['id']
        as_reloc = session.query(assignment_and_relocation_py.Assignment_and_relocation).filter_by(id=id).first()

        as_reloc.worker_id = worker_id
        as_reloc.date = flask.request.values['date']
        as_reloc.otdel = flask.request.values['otdel']  # Цех, отдел, участок
        as_reloc.prof = flask.request.values['prof'] # Профессия, должность
        as_reloc.sootvetst = flask.request.values['sootvetst']  # Соответствие специальности по диплому(свидетельству) занимаемой должности(профессии) (да, нет)
        as_reloc.razrad = flask.request.values['razrad'] # тарифный разрад
        as_reloc.uslov_truda = flask.request.values['uslov_truda']  # Условия труда
        # Основание
        as_reloc.osnov_doc = flask.request.values['osnov_doc'] # наименование документа
        as_reloc.osnov_date = flask.request.values['osnov_date']  # дата
        as_reloc.nomer = flask.request.values['nomer']  # Номер документа


        as_reloc.active = active

        as_reloc.date_edit = date_edit
        as_reloc.editor_id = editor_id

    try:
        session.add(as_reloc)
        session.commit()
    except Exception as e:
        logging.error(str(e))
        alert_html = Flask.mod.show_alert('danger', 'Ошибка! ', ' Не удалось обработать запрос с ошибкой: ' + str(e))

    session.close()

    return flask.redirect(flask.url_for('assignment_and_relocation', alert_html=alert_html, worker_id=worker_id, img_count=app.config['img_count']))






@app.route('/kvalif-up', methods=['GET', 'POST'])
def kvalif_up():
    alert_html = request.args.get('alert_html')
    worker_id = request.args.get('worker_id')
    if alert_html is None:
        alert_html = ''

    main_header = 'Повышение квалификации'
    session = Session()
    kvs = []
    kvalif = session.query(kvalif_up_py.Kvalif_up).filter_by(worker_id=worker_id).all()
    for ar in kvalif:
        ar.creator = session.query(clUser.User).filter_by(id=ar.creator_id).first()
        ar.editor = session.query(clUser.User).filter_by(id=ar.editor_id).first()
        kvs.append(ar)
    wor = session.query(worker_py.Worker).filter_by(id=worker_id).first()
    session.close()

    return render_template('add_edit_table/kvalif_up.html', kvalif=kvs,worker=wor ,main_header=main_header, alert_html=alert_html, img_count=app.config['img_count'])



@app.route('/kvalif-up-save', methods=['GET', 'POST'])
def kvalif_up_save():
    alert_html = Flask.mod.show_alert('success', 'Отлично! ', ' Данные сохранены')
    active = None
    session = Session()
    try:
        if flask.request.values['active'] == 'on':
            active = True
    except:
        active = False
    creator_id = flask_login.current_user.num
    date_create = datetime.now()
    editor_id = creator_id
    date_edit = date_create
    worker_id = flask.request.values['worker_id']

    if flask.request.values['id'] == 'add':
        kvalif = kvalif_up_py.Kvalif_up(worker_id=worker_id,
                              date=flask.request.values['date'],
                              type_kvalif = flask.request.values['type_kvalif'] ,
                              osnov_date = flask.request.values['osnov_date'] ,
                              nomer = flask.request.values['nomer'],
                              creator_id=creator_id,
                              date_create=date_create,
                              date_edit=date_edit,
                              editor_id=editor_id,
                              active=active)

    else:
        id = flask.request.values['id']
        kvalif = session.query(kvalif_up_py.Kvalif_up).filter_by(id=id).first()

        kvalif.worker_id = worker_id
        kvalif.date = flask.request.values['date']
        kvalif.type_kvalif = flask.request.values['type_kvalif']  # Цех, отдел, участок

        # Основание

        kvalif.osnov_date = flask.request.values['osnov_date']  # дата
        kvalif.nomer = flask.request.values['nomer']  # Номер документа


        kvalif.active = active

        kvalif.date_edit = date_edit
        kvalif.editor_id = editor_id

    try:
        session.add(kvalif)
        session.commit()
    except Exception as e:
        logging.error(str(e))
        alert_html = Flask.mod.show_alert('danger', 'Ошибка! ', ' Не удалось обработать запрос с ошибкой: ' + str(e))

    session.close()

    return flask.redirect(flask.url_for('kvalif_up', alert_html=alert_html, worker_id=worker_id, img_count=app.config['img_count']))






@app.route('/retraining', methods=['GET', 'POST'])
def retraining():
    alert_html = request.args.get('alert_html')
    worker_id = request.args.get('worker_id')
    if alert_html is None:
        alert_html = ''

    main_header = 'Переподготовка'
    session = Session()
    rets = []
    ret = session.query(retraining_py.Retraining).filter_by(worker_id=worker_id).all()
    for ar in ret:
        ar.creator = session.query(clUser.User).filter_by(id=ar.creator_id).first()
        ar.editor = session.query(clUser.User).filter_by(id=ar.editor_id).first()
        rets.append(ar)
    wor = session.query(worker_py.Worker).filter_by(id=worker_id).first()
    session.close()

    return render_template('add_edit_table/retraining.html', ret=rets,worker=wor ,main_header=main_header, alert_html=alert_html, img_count=app.config['img_count'])



@app.route('/retraining-save', methods=['GET', 'POST'])
def retraining_save():
    alert_html = Flask.mod.show_alert('success', 'Отлично! ', ' Данные сохранены')
    active = None
    session = Session()
    try:
        if flask.request.values['active'] == 'on':
            active = True
    except:
        active = False
    creator_id = flask_login.current_user.num
    date_create = datetime.now()
    editor_id = creator_id
    date_edit = date_create
    worker_id = flask.request.values['worker_id']

    if flask.request.values['id'] == 'add':
        ret = retraining_py.Retraining(worker_id=worker_id,
                              date=flask.request.values['date'],
                              special = flask.request.values['special'] ,
                              osnov_date = flask.request.values['osnov_date'] ,
                              nomer = flask.request.values['nomer'],
                              creator_id=creator_id,
                              date_create=date_create,
                              date_edit=date_edit,
                              editor_id=editor_id,
                              active=active)

    else:
        id = flask.request.values['id']
        ret = session.query(retraining_py.Retraining).filter_by(id=id).first()

        ret.worker_id = worker_id
        ret.date = flask.request.values['date']
        ret.special = flask.request.values['special']  # Цех, отдел, участок

        # Основание

        ret.osnov_date = flask.request.values['osnov_date']  # дата
        ret.nomer = flask.request.values['nomer']  # Номер документа


        ret.active = active

        ret.date_edit = date_edit
        ret.editor_id = editor_id

    try:
        session.add(ret)
        session.commit()
    except Exception as e:
        logging.error(str(e))
        alert_html = Flask.mod.show_alert('danger', 'Ошибка! ', ' Не удалось обработать запрос с ошибкой: ' + str(e))

    session.close()

    return flask.redirect(flask.url_for('retraining', alert_html=alert_html, worker_id=worker_id, img_count=app.config['img_count']))





@app.route('/vacation', methods=['GET', 'POST'])
def vacation():
    alert_html = request.args.get('alert_html')
    worker_id = request.args.get('worker_id')
    if alert_html is None:
        alert_html = ''

    main_header = 'Отпуска'
    session = Session()
    vs = []
    vacat = session.query(vacation_py.Vacation).filter_by(worker_id=worker_id).all()
    for ar in vacat:
        ar.creator = session.query(clUser.User).filter_by(id=ar.creator_id).first()
        ar.editor = session.query(clUser.User).filter_by(id=ar.editor_id).first()
        vs.append(ar)
    wor = session.query(worker_py.Worker).filter_by(id=worker_id).first()
    session.close()

    return render_template('add_edit_table/vacation.html', vacat=vs,worker=wor ,main_header=main_header, alert_html=alert_html, img_count=app.config['img_count'])



@app.route('/vacation-save', methods=['GET', 'POST'])
def vacation_save():
    alert_html = Flask.mod.show_alert('success', 'Отлично! ', ' Данные сохранены')
    active = None
    session = Session()
    try:
        if flask.request.values['active'] == 'on':
            active = True
    except:
        active = False
    creator_id = flask_login.current_user.num
    date_create = datetime.now()
    editor_id = creator_id
    date_edit = date_create
    worker_id = flask.request.values['worker_id']

    if flask.request.values['id'] == 'add':
        vacat = vacation_py.Vacation(worker_id=worker_id,
                              period=flask.request.values['period'],
                              osnov=flask.request.values['osnov'] ,
                              kolvo_dney=flask.request.values['kolvo_dney'] ,
                              dop_1=flask.request.values['dop_1'],
                              dop_2=flask.request.values['dop_2'],
                              dop_3=flask.request.values['dop_3'],
                              itog=flask.request.values['itog'] ,
                              vsego_dney=flask.request.values['vsego_dney'] ,
                              date_begin=flask.request.values['date_begin'] ,
                              date_end=flask.request.values['date_end'],
                              creator_id=creator_id,
                              date_create=date_create,
                              date_edit=date_edit,
                              editor_id=editor_id,
                              active=active)

    else:
        id = flask.request.values['id']
        vacat = session.query(vacation_py.Vacation).filter_by(id=id).first()

        vacat.worker_id = worker_id
        vacat.period = flask.request.values['period']
        vacat.osnov = flask.request.values['osnov']  # Основание
        vacat.kolvo_dney = flask.request.values['kolvo_dney']  # кол-во рабочих дней
        # Дополнительный отпуск
        vacat.dop_1 = flask.request.values['dop_1']
        vacat.dop_2 = flask.request.values['dop_2']
        vacat.dop_3 =flask.request.values['dop_3']
        vacat.itog = flask.request.values['itog']

        vacat.vsego_dney = flask.request.values['vsego_dney']
        # Дата
        vacat.date_begin = flask.request.values['date_begin'] # Дата начала основного и дополнительного отпуска
        vacat.date_end = flask.request.values['date_end'] # Дата окончания основного и дополнительного отпуска
        vacat.active = active

        vacat.date_edit = date_edit
        vacat.editor_id = editor_id

    try:
        session.add(vacat)
        session.commit()
    except Exception as e:
        logging.error(str(e))
        alert_html = Flask.mod.show_alert('danger', 'Ошибка! ', ' Не удалось обработать запрос с ошибкой: ' + str(e))

    session.close()

    return flask.redirect(flask.url_for('vacation', alert_html=alert_html, worker_id=worker_id, img_count=app.config['img_count']))


@app.route('/gen-worker-list', methods=['GET', 'POST'])
def genWorkerList():
    session = Session()
    worker_id = flask.request.values['worker_id']
    file_name = Flask.mod.genWorkerList(worker_id, session)

    return flask.redirect(workerlists_dir + file_name)

@app.route('/gen-personal-list', methods=['GET', 'POST'])
def genPersonalList():
    session = Session()
    worker_id = flask.request.values['worker_id']
    file_name = Flask.mod.genPersonalList(worker_id, session)

    return flask.redirect(personalList_dir + file_name)

@app.route('/gen-staff-list', methods=['GET', 'POST'])
def genStaffList():
    session = Session()
    file_name = Flask.mod.genStaffList(session)

    return flask.redirect(staffList_dir + file_name)



@app.route('/staff-list', methods=['GET', 'POST'])
def staff_list():
    alert_html = request.args.get('alert_html')

    if alert_html is None:
        alert_html = ''

    main_header = 'Штатное расписание'
    session = Session()
    ars = []
    stf_list = session.query(staff_list_py.Staff_list).all()
    for ar in stf_list:
        ar.creator = session.query(clUser.User).filter_by(id=ar.creator_id).first()
        ar.editor = session.query(clUser.User).filter_by(id=ar.editor_id).first()
        ars.append(ar)

    session.close()

    return render_template('add_edit_table/staff_list.html', staff_lists=ars,main_header=main_header, alert_html=alert_html, img_count=app.config['img_count'])



@app.route('/staff-list-save', methods=['GET', 'POST'])
def staff_list_save():
    alert_html = Flask.mod.show_alert('success', 'Отлично! ', ' Данные сохранены')
    active = None
    session = Session()
    try:
        if flask.request.values['active'] == 'on':
            active = True
    except:
        active = False
    creator_id = flask_login.current_user.num
    date_create = datetime.now()
    editor_id = creator_id
    date_edit = date_create

    kol_vo = flask.request.values['kol_vo']
    oklad = flask.request.values['oklad']
    nadbavka_1 = flask.request.values['nadbavka_1']
    nadbavka_2 = flask.request.values['nadbavka_2']
    nadbavka_3 = flask.request.values['nadbavka_3']
    fond = flask.request.values['fond']
    if Flask.mod.isint(kol_vo) == False:
        kol_vo = 0
    if Flask.mod.isint(oklad) == False:
        oklad = 0
    if Flask.mod.isint(nadbavka_1) == False:
        nadbavka_1 = 0
    if Flask.mod.isint(nadbavka_2) == False:
        nadbavka_2 = 0
    if Flask.mod.isint(nadbavka_3) == False:
        nadbavka_3 = 0
    if Flask.mod.isint(fond) == False:
        fond = 0

    if flask.request.values['id'] == 'add':
        stf_list = staff_list_py.Staff_list(name = flask.request.values['name'],
        dolzh = flask.request.values['dolzh'],
        kol_vo = kol_vo,
        oklad = oklad,
        nadbavka_1 = nadbavka_1,
        nadbavka_2 = nadbavka_2,
        nadbavka_3 = nadbavka_3,
        fond = fond,
        comment = flask.request.values['comment'],
                              creator_id=creator_id,
                              date_create=date_create,
                              date_edit=date_edit,
                              editor_id=editor_id,
                              active=active)

    else:
        id = flask.request.values['id']
        stf_list = session.query(staff_list_py.Staff_list).filter_by(id=id).first()

        stf_list.name = flask.request.values['name']#наименование
        stf_list.dolzh = flask.request.values['dolzh']#должность
        stf_list.kol_vo = kol_vo #количество штатных единиц
        stf_list.oklad = oklad #оклад, тарифная ставка(тенге)
        stf_list.nadbavka_1 = nadbavka_1 #надбавка(тенге)
        stf_list.nadbavka_2 = nadbavka_2 #надбавка(тенге)
        stf_list.nadbavka_3 = nadbavka_3 #надбавка(тенге)
        stf_list.fond = fond  ##Месячный фонд(тенге)
        stf_list.comment = flask.request.values['comment']  #Примечание



        stf_list.active = active

        stf_list.date_edit = date_edit
        stf_list.editor_id = editor_id

    try:
        session.add(stf_list)
        session.commit()
    except Exception as e:
        logging.error(str(e))
        alert_html = Flask.mod.show_alert('danger', 'Ошибка! ', ' Не удалось обработать запрос с ошибкой: ' + str(e))

    session.close()

    return flask.redirect(flask.url_for('staff_list', alert_html=alert_html, img_count=app.config['img_count']))




@app.route('/notes-save', methods=['GET', 'POST'])
def notes_save():
    alert_html = Flask.mod.show_alert('success', 'Отлично! ', ' Данные сохранены')
    active = None
    session = Session()
    try:
        if flask.request.values['active'] == 'on':
            active = True
    except:
        active = False
    creator_id = flask_login.current_user.num
    date_create = datetime.now()
    editor_id = creator_id
    date_edit = date_create
    text = flask.request.values['text']
    ret = ''

    if flask.request.values['id'] == 'add':
        ret = notes_py.Notes(text=text,
                              creator_id=creator_id,
                              date_create=date_create,
                              date_edit=date_edit,
                              editor_id=editor_id,
                              active=active)



    try:
        session.add(ret)
        session.commit()
    except Exception as e:
        logging.error(str(e))
        alert_html = Flask.mod.show_alert('danger', 'Ошибка! ', ' Не удалось обработать запрос с ошибкой: ' + str(e))

    session.close()

    return flask.redirect(flask.url_for('home', alert_html=alert_html, img_count=app.config['img_count']))







@app.route('/upload-user-pic', methods=['GET', 'POST'])
def upload_user_pic():
        app.config['img_count'] = app.config['img_count'] + 1
        user_id = flask.request.values['id']
        file = flask.request.files['file']
        if file:
            filename = app.config['UPLOAD_FOLDER'] + str(user_id)+".png"
            file.save(filename)

        return flask.redirect(flask.url_for('user_edit',id=user_id, img_count=app.config['img_count']))


@app.route('/upl', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        file = request.files['file']
        if file and Flask.mod.allowed_file(file.filename):
            filename = file.filename
            file.save(app.config['UPLOAD_FOLDER'] + "1.png")
            return flask.redirect(flask.url_for('uploaded_file', filename=filename))
    return '''
<!doctype html>
<title>Загрузить новый файл</title>
<h1>Загрузить новый файл</h1>
<form action="/upl" method=post enctype=multipart/form-data>
  <p><input type=file name=file>
    <input type=submit value="Загрузить">
</form>

'''


@app.route('/rep1', methods=['GET', 'POST'])
def genRep1():
    today = datetime.today()
    today = today.strftime("%Y-%m-%d")
    logging.debug('today: ' + today)
    main_header = 'Отчет по работникам (в отпуске/в штате) на текущий момент или на выбранную дату'
    alert_html = request.args.get('alert_html')
    if alert_html is None:
        alert_html = ''
    if request.method != 'POST':
        return render_template('reports/rep1.html', main_header=main_header, alert_html=alert_html, date=today)
    else:
        type = flask.request.values['type_report']
        session = Session()
        type_date = flask.request.values['type_date']
        if type_date == '0':
            pass
            logging.debug('today: ' + today)
        elif type_date == '1':
            date = flask.request.values['date']
            today = date
            logging.debug('Date: ' + today)
        else:
            today = ''
            logging.debug('date empty: ' + today)
        workers_count = session.execute('select count(id) from worker').first()[0]
        sql_vac_count = "SELECT count(worker_id) FROM vacation " \
          "right join worker on worker.id = vacation.worker_id " \
          "where "+"'"+today+"'"+  " between vacation.date_begin and vacation.date_end group by worker_id"
        try:
            vac_count = session.execute(sql_vac_count).first()[0]
        except:
            vac_count  = 0
        worked_count = workers_count - vac_count
        if type == '0':
            sql_vac_list = "SELECT * FROM vacation right join worker on worker.id = vacation.worker_id " \
                "where " + "'" + today + "'" + " between vacation.date_begin and vacation.date_end group by worker_id "
            vac_list = session.execute(sql_vac_list)
            #logging.error("Vac_sql: " + sql)
            text = 'По состоянию на '+ today +' , всего работников - ' + str(workers_count) + ', из них: ' \
                                                                '\n в штате - ' + str(worked_count) + ', ' \
                                                                '\nв отпуске - ' + str(vac_count) + '. \n' \
                                                                 'Список работников в отпуске:'

            return render_template('reports/rep1.html', main_header=main_header, workers_count=workers_count,
                                   vac_count=vac_count, worked_count=worked_count, vac_list=vac_list, alert_html=alert_html,
                                   type_report=type, text=text)

        if type == '1':
            sql_vac_list = "SELECT * FROM vacation right join worker on worker.id = vacation.worker_id " \
                           "where " + "'" + today + "'" + " not between vacation.date_begin and vacation.date_end group by worker_id"
            vac_list = session.execute(sql_vac_list)
            # logging.error("Vac_sql: " + sql)
            text = 'По состоянию на '+ today +' , всего работников - ' + str(workers_count) +', из них: ' \
                                                                '\n в штате - ' + str(worked_count) +',' \
                                                                '\nв отпуске - ' + str(vac_count) +'. \n' \
                                                                'Список работников в штате:'
            return render_template('reports/rep1.html', main_header=main_header, workers_count=workers_count,
                                   vac_count=vac_count, worked_count=worked_count, vac_list=vac_list,
                                   alert_html=alert_html, type_report=type, text=text, type_date=type_date, date=today)
        else:
            pass

        return render_template('reports/rep1.html', main_header=main_header, alert_html=alert_html)





@app.route('/rep2', methods=['GET', 'POST'])
def genRep2():
    post = 0
    today = datetime.today()
    today = today.strftime("%Y-%m-%d")
    logging.debug('today: ' + today)
    main_header = 'Отчет о назначениях и перемещениях сотрудников по диапазону дат'
    alert_html = request.args.get('alert_html')
    if alert_html is None:
        alert_html = ''
    if request.method != 'POST':

        return render_template('reports/rep2.html', main_header=main_header, alert_html=alert_html, date=today)
    else:
        post = 1
        session = Session()
        date1 = flask.request.values['date1']
        date2 = flask.request.values['date2']
        sql = "SELECT * FROM assignment_and_relocation " \
                           "right join worker on worker.id = assignment_and_relocation.worker_id " \
                           "where assignment_and_relocation.date between " + "'" + date1 + "'" + " and " + "'" + date2 + "'" + ""

        res = session.execute(sql)
        return render_template('reports/rep2.html', main_header=main_header, alert_html=alert_html, res=res, post=post, date1=date1, date2=date2)

