# coding:utf-8

import logging
import os
import re
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr
import zipfile

from flask import flash, jsonify, request, current_app, url_for
from flask_login import login_required, login_user, current_user

from . import app, db
from .APIError import (APIPermissionError, APIResourceNotFoundError,
                       APIValueError)
from .models import User, Permission, Role
from .tools import secure_filename, permission_required, admin_required

logging.basicConfig(level=logging.INFO)


@app.route('/api/signup', methods=['POST'])
def api_signup():
    name = request.json['name']
    email = request.json['email']
    password = request.json['password']
    u = User.query.filter_by(email=email).first()
    if u is not None:
        raise APIValueError('email', '该email已被注册！')
    u = User(name=name, email=email, password=password)
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
        if u.role_r.default:
            flash('请联系管理员确认身份')
        return jsonify({'name': u.name})
    else:
        raise APIValueError('password', '密码错误！')


@app.route('/api/modify_password', methods=['POST'])
def api_modify_password():
    email = request.json['email']
    password0 = request.json['password0']
    password1 = request.json['password1']
    password2 = request.json['password2']
    u = User.query.filter_by(email=email).first()
    if u is None:
        raise APIPermissionError('密码修改失败！用户不存在。')
    elif password1 != password2:
        raise APIPermissionError('密码修改失败！两次输入的密码不一致。')
    elif not u.verify_password(password0):
        raise APIPermissionError('密码修改失败！旧密码不正确。')
    else:
        u.password = password1
        db.session.add(u)
        db.session.commit()
        flash('密码修改成功请重新登录')
        return jsonify({'name': u.name})


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


@app.route('/api/forgot_password', methods=['POST'])
def api_forgot_password():
    from_addr = current_app.config['EMAIL_FROM']
    password = current_app.config['EMAIL_PWORD']
    to_addr = request.json['email']
    smtp_server = current_app.config['SMTP_SRV']
    smtp_port = current_app.config['SMTP_PORT']
    u = User.query.filter_by(email=to_addr).first()
    token = u.generate_forgot_token()
    url = url_for('forgot_password', email=to_addr, token=token, _external=True)
    # 发送email
    msg = MIMEText('重设密码需要确认您的身份，请复制以下链接地址至浏览器中:\n' + url, 'plain', 'utf-8')
    msg['From'] = _format_addr('管理员 <%s>' % from_addr)
    msg['To'] = _format_addr('%s <%s>' % (u.name, to_addr))
    msg['Subject'] = Header('来自 ' + current_app.config['WEB_NAME'] + ' - 重设密码', 'utf-8').encode()
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()
    return jsonify({'email': to_addr})


@app.route('/api/upload', methods=['POST'])
@login_required
@permission_required(Permission.FILE_UPDOWN)
def api_upload():
    file = request.files['file']
    if file is None:
        APIResourceNotFoundError('file', '未接收到上传的文件！')
    filename = secure_filename(file.filename)
    dir = str(current_user.id) + '-' + current_user.name
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], dir, filename))
    return jsonify({'done': True})


def todir(filename):
    if filename.startswith('HT.HRCS') or filename.startswith('HRCS') or filename.startswith('HT.RSCS'):
        return 'HRCS'
    if filename.startswith('HT'):
        s = re.match(r'^(HT\.[\S])', filename, re.M | re.I)
        return s.group(1)
    else:
        s = re.match(r'^([\S])', filename, re.M | re.I)
        return s.group(1)
    return filename[0]


@app.route('/api/archive', methods=['POST'])
@login_required
@permission_required(Permission.DWG_UPDOWN)
def api_archive():
    file = request.files['file']
    if file is None:
        APIResourceNotFoundError('file', '未接收到上传的文件！')
    filename = secure_filename(file.filename)
    path = os.path.join(current_app.config['DWG_DIR'], todir(filename))
    if not os.path.isdir(path):
        os.mkdir(path)
    file.save(os.path.join(path, filename))
    return jsonify({'done': True})


@app.route('/api/download', methods=['POST'])
@login_required
@permission_required(Permission.DWG_UPDOWN)
def api_download():
    dir = request.json['dir']
    filenamelist = request.json['filename']
    if len(filenamelist) > 1:
        zfname = os.path.join(current_app.config['TMP_DIR'], request.remote_addr.replace('.', '-') + '.zip')
        zf = zipfile.ZipFile(os.path.join('myapp/static/', zfname), 'w', zipfile.ZIP_DEFLATED, False)
        for filename in filenamelist:
            zf.write(os.path.join(current_app.config['DWG_DIR'], dir, filename), filename)
        zf.close()
        return jsonify({'url': url_for('static', filename=zfname)})
    else:
        return jsonify({'url': url_for('download_file', dir=dir, filename=filenamelist[0])})


@app.route('/api/delete', methods=['POST'])
@login_required
@permission_required(Permission.DWG_UPDOWN)
def api_delete():
    dir = request.json['dir']
    filenamelist = request.json['filename']
    for filename in filenamelist:
        os.remove(os.path.join(current_app.config['DWG_DIR'], dir, filename))
    return jsonify({'done': True})


@app.route('/api/users')
@login_required
@admin_required
def api_users():
    users = User.query.all()
    return jsonify({'users': [user.to_json() for user in users]})


@app.route('/api/roles')
@login_required
@admin_required
def api_roles():
    roles = Role.query.all()
    return jsonify({'roles': [role.to_json() for role in roles]})


@app.route('/api/del_user', methods=['POST'])
@login_required
@admin_required
def api_del_user():
    email = request.json['email']
    u = User.query.filter_by(email=email).first()
    if u is None:
        raise APIResourceNotFoundError('email', '没有此email对应的用户')
    db.session.delete(u)
    db.session.commit()
    return jsonify({'name': u.name})


@app.route('/api/edit_user', methods=['POST'])
@login_required
@admin_required
def api_edit_user():
    email = request.json['email']
    role_name = request.json['role_name']
    u = User.query.filter_by(email=email).first()
    if u is None:
        raise APIResourceNotFoundError('email', '没有此email对应的用户!')
    r = Role.query.filter_by(name=role_name).first()
    if r is None:
        raise APIResourceNotFoundError('role_name', '没有此身份!')
    u.role_r = r
    db.session.add(u)
    db.session.commit()
    if (r.permission | Permission.DEFAULT) != Permission.DEFAULT:
        dir = str(u.id) + '-' + u.name
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], dir)
        if not os.path.isdir(path):
            os.mkdir(path)
    return jsonify({'name': u.name})
