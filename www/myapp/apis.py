import logging
from flask import request, jsonify, flash
from flask_login import login_user
from . import app, db
from .models import User, Role
logging.basicConfig(level=logging.INFO)


@app.route('/api/signup', methods=['POST'])
def api_signup():
    name = request.json['name']
    email = request.json['email']
    password = request.json['password']
    r = Role.query.filter_by(name='user').first()
    u = User(name=name, email=email, password=password, role_r=r)
    db.session.add(u)
    db.session.commit()
    flash('注册成功请登录')
    return jsonify({'name': name})


@app.route('/api/login', methods=['POST'])
def api_login():
    email = request.json['email']
    password = request.json['password']
    rememberme = request.json['rememberme']
    print(rememberme)
    u = User.query.filter_by(email=email).first()
    if u is not None and u.verify_password(password):
        login_user(u, rememberme)
        return jsonify({'name': u.name})
    flash('用户名或者密码错误！')
    return jsonify({'name': ''})

