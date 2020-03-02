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
from flask_uploads import UploadSet, configure_uploads, IMAGES,UploadNotAllowed
UPLOADED_PHOTOS_DEST_USER = '/files/photo/user'
app.config.from_object(__name__)
app.config.from_envvar('PHOTOLOG_SETTINGS', silent=True)
uploaded_photos = UploadSet('photos', IMAGES)
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
    user.image_name = user_cl.image_name


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
        user.image_name = user_cl.image_name

        # DO NOT ever store passwords in plaintext and always compare password
        # hashes using constant-time comparison!
        user.is_authenticated = (flask.request.form['password'] == user_cl.password) and (user.active == 1)

        return user
    except:
        return




# users = {'foo@bar.tld': {'password': 'secret'}}



@app.route('/')
def home():
    session = Session()
    alert = Flask.mod.show_alert('danger', 'Привет!', 'Это главная страница!')
    try:
        user = flask_login.current_user.nickname

    except:
        user = 'Гость'
        return flask.redirect(flask.url_for('login_form'))

    return render_template('index.html',  user=user, html_alert=alert)


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
        user.image_name = user_cl.image_name

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
    session = Session()
    users = session.query(clUser.User).all()
    return render_template('/tables/user.html', users=users)

@app.route('/user/add', methods=['GET', 'POST'])
def user_add():
    return render_template('/add_edit_table/user.html')

@app.route('/user/edit', methods=['GET', 'POST'])
def user_edit():
    session = Session()
    id = flask.request.values['id']
    user_cl = session.query(clUser.User).filter_by(id=id).first()
    return render_template('/add_edit_table/user.html', user_cl=user_cl)

@app.route('/user/save', methods=['GET', 'POST'])
def user_save():
    session = Session()
    users = session.query(clUser.User).all()
    return render_template('/add_edit_table/user.html', users=users)