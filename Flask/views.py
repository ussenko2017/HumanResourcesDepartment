# -*- coding: utf-8 -*-

from datetime import datetime
from flask import render_template, jsonify,request
from Flask import app
import json
import random
import requests
import Flask.mod
from table_class import user as clUser
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine, DateTime, inspect
import flask
import flask_login
from config import SQLALCHEMY_DB_URI, DEBUG
from flask import render_template, g

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
    session.commit()

    users = session.query(clUser.User).all()
    alert_html = Flask.mod.show_alert('success', 'Отлично! ', 'Пользовательские данные сохранены')
    return flask.redirect(flask.url_for('user', alert_html=alert_html))
