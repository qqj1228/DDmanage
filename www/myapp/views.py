# coding:utf-8

import logging
import os
import re
import shutil

from flask import flash, redirect, render_template, request, url_for, send_from_directory, current_app
from flask_login import login_required, logout_user, current_user

from . import app
from .models import User, Permission
from .tools import admin_required, permission_required

logging.basicConfig(level=logging.INFO)
DWG_DIR = app.config.get('DWG_DIR')
TMP_DIR = app.config.get('TMP_DIR')
RANGE = app.config.get('RANGE')


# 把Permission类加入模板上下文
@app.context_processor
def inject_permissions():
    return dict(Permission=Permission)


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.errorhandler(403)
def Forbidden(e):
    return render_template('403.html'), 403


def getdir(dir=DWG_DIR):
    dirlist_out = []
    dirlist = os.listdir(dir)
    for dir in dirlist:
        if os.path.isdir(os.path.join(DWG_DIR, dir)):
            dirlist_out.append(dir)
    return dirlist_out


def getfile(dir=DWG_DIR):
    filelist_out = []
    filelist = os.listdir(dir)
    for file in filelist:
        if os.path.isfile(os.path.join(dir, file)):
            if file[0] != '.':    # 去掉以“.”开头的隐藏文件
                filelist_out.append(file)
    return filelist_out


def getpage(filelist, page_cu):
    page = dict()
    file_count = len(filelist)
    page_all = file_count // RANGE + (1 if file_count % RANGE else 0)
    page_start = RANGE * (page_cu - 1)
    page['range'] = RANGE
    page['file_count'] = file_count
    page['page_all'] = page_all
    page['page_start'] = page_start
    return page


@app.route('/')
@app.route('/<dir_cu>/<int:page_cu>')
def index(dir_cu='', page_cu=1):
    dirlist = getdir()
    filelist = getfile(os.path.join(DWG_DIR, dir_cu))
    page = getpage(filelist, page_cu)
    args = dict()
    args['dirlist'] = dirlist
    args['filelist'] = filelist
    args['dir_cu'] = dir_cu
    args['page_cu'] = page_cu
    args['page'] = page
    return render_template('index.html', args=args)


@app.route('/show/<dir>/<filename>')
@login_required
@permission_required(Permission.DWG_BROWSE)
def show(dir, filename):
    if re.search(r'\.d[wx][gft]$', filename, re.M | re.I):
        return redirect(url_for('showdwg', dir=dir, filename=filename))
    elif re.search(r'\.pdf$', filename, re.I):
        return redirect(url_for('showpdf', dir=dir, filename=filename))
    else:
        flash('无法打开 "' + filename + '"，暂未支持该文件格式。')
        return redirect(url_for('index', dir_cu=dir, page_cu=1))


@app.route('/showdwg/<dir>/<filename>')
@login_required
@permission_required(Permission.DWG_BROWSE)
def showdwg(dir, filename):
    args = dict()
    source = os.path.join(DWG_DIR, dir, filename)
    dest = os.path.join(TMP_DIR, request.remote_addr.replace('.', '-'))
    shutil.copy(source, os.path.join('myapp/static/', dest))
    url = url_for('static', filename=dest, _external=True)
    args['filename'] = filename
    args['url'] = url
    return render_template('showdwg.html', args=args)


@app.route('/showpdf/<dir>/<filename>')
@login_required
@permission_required(Permission.DWG_BROWSE)
def showpdf(dir, filename):
    source = os.path.join(DWG_DIR, dir, filename)
    dest = os.path.join(TMP_DIR, request.remote_addr.replace('.', '-') + '.pdf')
    shutil.copy(source, os.path.join('myapp/static/', dest))
    # return redirect(url_for('static', filename=dest))
    url = url_for('static', filename=dest)
    args = dict()
    args['filename'] = filename
    args['url'] = url
    return render_template('showpdf.html', args=args)


@app.route('/download/<dir>/<filename>/<personal>')
@login_required
@permission_required(Permission.FILE_UPDOWN)
def download_file(dir, filename, personal):
    if personal == 'personal':
        path_abs = os.path.join(current_app.config['UPLOAD_FOLDER'], dir)
    else:
        path_abs = os.path.join(current_app.config['DWG_DIR'], dir)
    return send_from_directory(path_abs, filename=filename, as_attachment=True)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已退出本程序')
    return redirect(url_for('login'))


@app.route('/manage')
@app.route('/manage/<int:page_cu>')
@login_required
@permission_required(Permission.DWG_BROWSE)
def manage(page_cu=1):
    dir = str(current_user.id) + '-' + current_user.name
    filelist = getfile(os.path.join(current_app.config['UPLOAD_FOLDER'], dir))
    page = getpage(filelist, page_cu)
    args = dict()
    args['filelist'] = filelist
    args['dir'] = dir
    args['page_cu'] = page_cu
    args['page'] = page
    return render_template('manage.html', args=args)


@app.route('/user')
@login_required
def user():
    return render_template('user.html')


@app.route('/forgot_password/<email>/<token>')
def forgot_password(email, token):
    u = User.query.filter_by(email=email).first()
    if not u.verify_forgot_token(token):
        flash('验证失败或已过期！')
        return redirect(url_for('login'))
    return render_template('forgot_password.html', email=u.email)


@app.route('/admin')
@login_required
@admin_required
def admin():
    return render_template('admin.html')
