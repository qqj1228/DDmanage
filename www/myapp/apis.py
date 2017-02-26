import logging
import os
from flask import request, jsonify, flash
from flask_login import login_user, login_required
from . import app, db
from .models import User, Role
from .tools import secure_filename
from .APIError import APIValueError, APIResourceNotFoundError, APIPermissionError
logging.basicConfig(level=logging.INFO)


@app.route('/api/signup', methods=['POST'])
def api_signup():
    name = request.json['name']
    email = request.json['email']
    password = request.json['password']
    r = Role.query.filter_by(name='user').first()
    confirmed = False
    u = User.query.filter_by(email=email).first()
    if u is not None:
        raise APIValueError('email', '该email已被注册！')
    u = User(name=name, email=email, password=password, role_r=r, confirmed=confirmed)
    db.session.add(u)
    db.session.commit()
    flash('注册成功请登录')
    return jsonify({'name': name})


@app.route('/api/login', methods=['POST'])
def api_login():
    email = request.json['email']
    password = request.json['password']
    rememberme = request.json['rememberme']
    u = User.query.filter_by(email=email).first()
    if u is not None and u.verify_password(password):
        login_user(u, rememberme)
        flash('用户: %s 已登录' % u.name)
        return jsonify({'name': u.name})
    else:
        raise APIValueError('password', '密码错误！')


@app.route('/api/modify_password', methods=['POST'])
@login_required
def api_modify_password():
    id = request.json['user_id']
    password0 = request.json['password0']
    password1 = request.json['password1']
    password2 = request.json['password2']
    u = User.query.get(id)
    if u is not None and u.verify_password(password0) and password1 == password2:
        u.password = password1
        db.session.add(u)
        db.session.commit()
        flash('密码修改成功请重新登录')
        return jsonify({'user_id': id})
    else:
        raise APIPermissionError('密码修改失败！可能的原因为：1、用户不存在。2、旧密码不正确。3、两次输入的密码不一致')


@app.route('/api/reset_password', methods=['POST'])
def api_reset_password():
    id = request.json['user_id']
    password0 = request.json['password0']
    password1 = request.json['password1']
    password2 = request.json['password2']
    u = User.query.get(id)
    if u is not None and u.verify_password(password0) and password1 == password2:
        u.password = password1
        db.session.add(u)
        db.session.commit()
        flash('密码修改成功请重新登录')
        return jsonify({'user_id': id})
    else:
        raise APIPermissionError('密码修改失败！可能的原因为：1、用户不存在。2、旧密码不正确。3、两次输入的密码不一致')


@app.route('/api/upload', methods=['POST'])
@login_required
def api_upload():
    file = request.files['file']
    if file is None:
        APIResourceNotFoundError('file', '未接收到上传的文件！')
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return jsonify({'done': True})
