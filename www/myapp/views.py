# coding:utf-8

import logging
import os
import re
import shutil
from urllib.parse import quote

from flask import flash, redirect, render_template, url_for, send_from_directory, current_app
from flask_login import login_required, logout_user, current_user

from . import app
from .models import User, Permission
from .tools import admin_required, permission_required, secure_filename

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
    dirlist_out.sort()
    return dirlist_out


def getfile(dir=DWG_DIR):
    filelist_out = []
    filelist = os.listdir(dir)
    for file in filelist:
        if os.path.isfile(os.path.join(dir, file)):
            if file[0] != '.':    # 去掉以“.”开头的隐藏文件
                filelist_out.append(file)
    filelist_out.sort()
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
def index():
    return redirect(url_for('about'))


@app.route('/browse')
@app.route('/browse/<dir_cu>/<int:page_cu>')
@login_required
def browse(dir_cu='', page_cu=1):
    dirlist = getdir()
    filelist = getfile(os.path.join(DWG_DIR, dir_cu))
    page = getpage(filelist, page_cu)
    args = dict()
    args['dirlist'] = dirlist
    args['filelist'] = filelist
    args['dir_cu'] = dir_cu
    args['page_cu'] = page_cu
    args['page'] = page
    return render_template('browse.html', args=args)


@app.route('/show/<dir>/<filename>/<personal>')
@login_required
@permission_required(Permission.DWG_BROWSE)
def show(dir, filename, personal):
    raw = r'\.(pdf|jpg|jpeg|jpe|png|gif|ico|svg|tif|tiff|bmp|txt|doc|docx|xls|xlsx|ppt|pptx)$'
    if re.search(r'\.d[wx][gft]$', filename, re.M | re.I):
        return redirect(url_for('showdwg', dir=dir, filename=filename, personal=personal))
    elif re.search(raw, filename, re.M | re.I):
        return redirect(url_for('showpdf', dir=dir, filename=filename, personal=personal))
    else:
        flash('无法打开 "' + filename + '"，暂未支持该文件格式。')
        if personal == 'personal':
            rv = redirect(url_for('manage', page_cu=1))
        else:
            rv = redirect(url_for('browse', dir_cu=dir, page_cu=1))
        return rv


@app.route('/showdwg/<dir>/<filename>/<personal>')
@login_required
@permission_required(Permission.DWG_BROWSE)
def showdwg(dir, filename, personal):
    args = dict()
    if personal == 'personal':
        source = os.path.join(current_app.config['UPLOAD_FOLDER'], dir, filename)
    else:
        source = os.path.join(DWG_DIR, dir, filename)
    dest = os.path.join(TMP_DIR, str(current_user.id))
    shutil.copy(source, os.path.join('myapp/static/', dest))
    url = url_for('static', filename=dest, _external=True)
    args['filename'] = filename
    args['url'] = url
    return render_template('showdwg.html', args=args)


@app.route('/showpdf/<dir>/<filename>/<personal>')
@login_required
@permission_required(Permission.DWG_BROWSE)
def showpdf(dir, filename, personal):
    if personal == 'personal':
        source = os.path.join(current_app.config['UPLOAD_FOLDER'], dir, filename)
    else:
        source = os.path.join(DWG_DIR, dir, filename)
    addr_name = str(current_user.id)
    name_ext = os.path.splitext(filename)
    filelist = os.listdir(os.path.join(current_app.root_path, 'static/', TMP_DIR))
    for file in filelist:
        if file.startswith(addr_name):
            os.remove(os.path.join(current_app.root_path, 'static/', TMP_DIR, file))
    dest = os.path.join(TMP_DIR, addr_name + '_' + name_ext[0] + name_ext[1])
    shutil.copy(source, os.path.join('myapp/static/', dest))
    # return redirect(url_for('static', filename=dest))
    url = url_for('static', filename=dest)
    args = dict()
    args['filename'] = filename
    args['url'] = url
    return render_template('showpdf.html', args=args)


@app.route('/download/<path:dir>/<filename>/<personal>')
@login_required
@permission_required(Permission.FILE_UPDOWN)
def download_file(dir, filename, personal):
    if personal == 'personal':
        dir_abs = os.path.join(current_app.config['UPLOAD_FOLDER'], dir)
        hidden_path = os.path.join('/personal', dir, filename)
    else:
        dir_abs = os.path.join(current_app.config['DWG_DIR'], dir)
        hidden_path = os.path.join('/dwg', dir, filename)
    # 对文件名进行转码
    fname_encoded = quote(filename)
    options = dict()
    options['conditional'] = True
    options['as_attachment'] = True
    options['attachment_filename'] = fname_encoded
    rv = send_from_directory(dir_abs, filename, **options)
    # 支持中文名称
    if fname_encoded == filename:
        rv.headers['Content-Disposition'] += "; filename*=utf-8''%s" % fname_encoded
    # 使用nginx处理静态文件
    if current_app.config['USE_X_SENDFILE'] and current_app.config['NGINX']:
        rv.headers['X-Accel-Redirect'] = hidden_path
    return rv


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
    dir = current_user.email
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
@app.route('/admin/user')
@login_required
@admin_required
def admin_user():
    return render_template('admin_user.html')


@app.route('/admin/record')
@login_required
@admin_required
def admin_record():
    return render_template('admin_record.html')


def findfile(start, name):
    filelist = []
    s = name.replace('(', '\(')
    s = s.replace(')', '\)')
    for relpath, dirs, files in os.walk(start):
        for file in files:
            if file[0] != '.':    # 去掉以“.”开头的隐藏文件
                name_ext = os.path.splitext(file)
                if re.search(s, name_ext[0], re.M | re.I) is not None:
                    path = relpath.lstrip(start)
                    filelist.append((path, file))
    filelist.sort(key=lambda x: x[1])
    return filelist


@app.route('/search/<text>')
@app.route('/search/<text>/<int:page_cu>')
@login_required
@permission_required(Permission.DWG_BROWSE)
def search(text, page_cu=1):
    dirlist = getdir()
    text = secure_filename(text.strip())
    filelist = findfile(current_app.config['DWG_DIR'], text)
    page = getpage(filelist, page_cu)
    args = dict()
    args['dirlist'] = dirlist
    args['dir_cu'] = ''
    args['text'] = text
    args['page_cu'] = page_cu
    args['page'] = page
    return render_template('search.html', text=text, filelist=filelist, args=args)
