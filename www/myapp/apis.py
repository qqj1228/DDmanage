import logging
import os
from flask import request, jsonify, flash
from flask_login import login_user
from . import app, db
from .models import User, Role
from .tools import secure_filename
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
        flash('用户：%s 已登录' % u.name)
        return jsonify({'name': u.name})
    else:
        flash('用户名或者密码错误！')
        return jsonify({'name': ''})


@app.route('/api/upload', methods=['POST'])
def api_upload():
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return jsonify({'ok': ''})
