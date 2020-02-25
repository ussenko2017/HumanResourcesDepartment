# -*- coding: utf-8 -*-
"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, jsonify,request
from Flask import app
import json
import random
import requests
from table_class import user as clUser

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine, DateTime, inspect

# -*- coding: utf-8 -*-
"""
This script runs the Flask application using a development server.
"""

from datetime import datetime

import flask
import flask_login
from config import SQLALCHEMY_DB_URI
from flask import render_template, g
import config

login_manager = flask_login.LoginManager()

login_manager.init_app(app)


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    engine = create_engine(SQLALCHEMY_DB_URI, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        user_cl = session.query(clUser.User).filter_by(email=email).all()[0]
    except:
        user_cl = None
    if user_cl == None:
        return
    user = User()
    user.id = email
    user.num = user_cl.id
    user.firstname = user_cl.firstname
    user.lastname = user_cl.lastname
    user.patr = user_cl.patr
    user.birthday = user_cl.birthday
    user.nickname = user_cl.nickname
    user.password = user_cl.password
    quer = 'SELECT COUNT(teacher.user_id) as num FROM teacher WHERE teacher.user_id = ' + str(user_cl.id)
    numb = session.execute(quer)
    access = False
    for i in numb:
        if i[0] == 1:
            access = True
    user.access = access


    return user


@login_manager.request_loader
def request_loader(request):
    engine = create_engine(SQLALCHEMY_DB_URI, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    email = request.form.get('email')
    try:
        user_cl = session.query(clUser.User).filter_by(email=email).all()[0]
    except:
        user_cl = None
    if user_cl == None:
        return

    user = User()
    user.id = email
    user.num = user_cl.id
    user.firstname = user_cl.firstname
    user.lastname = user_cl.lastname
    user.patr = user_cl.patr
    user.birthday = user_cl.birthday
    user.nickname = user_cl.nickname
    user.password = user_cl.password
    quer = 'SELECT COUNT(teacher.user_id) as num FROM teacher WHERE teacher.user_id = ' + str(user_cl.id)
    numb = session.execute(quer)
    access = False
    for i in numb:
        if i[0] == 1:
            access = True
    user.access = access

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = flask.request.form['password'] == user_cl.password

    return user


# users = {'foo@bar.tld': {'password': 'secret'}}



@app.route('/')
def home():
    engine = create_engine(SQLALCHEMY_DB_URI, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()



    try:
        user = flask_login.current_user.id
    except:
        user = 'null'
    return render_template('index.html',  user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    engine = create_engine(SQLALCHEMY_DB_URI, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    email = request.form.get('email')
    try:
        user_cl = session.query(clUser.User).filter_by(email = email).all()[0]
        print(user_cl)

    except:
        user_cl = None
    if user_cl != None and flask.request.form['password'] == user_cl.password:
        user = User()
        user.id = email
        user.num = user_cl.id
        user.firstname = user_cl.firstname
        user.lastname = user_cl.lastname
        user.patr = user_cl.patr
        user.birthday = user_cl.birthday
        user.nickname = user_cl.nickname
        user.password = user_cl.password
        quer = 'SELECT COUNT(teacher.user_id) as num FROM teacher WHERE teacher.user_id = '+ str(user_cl.id)
        numb = session.execute(quer)
        access = False
        for i in numb:
            if i[0] == 1:
                access = True
        user.access = access
        flask_login.login_user(user)



        return flask.redirect(flask.url_for('home'))

    return flask.redirect(flask.url_for('home'))


@app.route('/profile')
@flask_login.login_required
def profile():
    return render_template('profile.html',user=flask_login.current_user)


@app.route('/logout')
def logout():
    flask_login.logout_user()
    g.user = 'Гость'
    return flask.redirect(flask.url_for('home'))


@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'


@app.route('/reg', methods=['GET', 'POST'])
def reg():
    engine = create_engine(SQLALCHEMY_DB_URI, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    email = flask.request.form['email']
    password = flask.request.form['password']


    try:
        user_cl = session.query(clUser.User).filter_by(email=email).all()[0]
    except:
        user_cl = None

    if user_cl == None:
        us = clUser.User('',email,password,'','','','')
        session.add(us)
        session.commit()
        g.user = email


        return flask.redirect(flask.url_for('home'))

    return flask.redirect(flask.url_for('home'))



@app.route('/del', methods=['GET', 'POST'])
def delete():
    engine = create_engine(SQLALCHEMY_DB_URI, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    id = flask.request.values['id']
    redirect = flask.request.values['redirect']
    tablename = flask.request.values['tablename']
    sql = "DELETE FROM `" + tablename + "` WHERE `" + tablename+"`.id = " + id
    session.execute(sql)
    session.commit()
    return flask.redirect(redirect)
