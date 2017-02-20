import logging
import os
import shutil
import re
from flask import render_template, request, url_for, redirect, flash
from myapp import app


logging.basicConfig(level=logging.INFO)
DWG_DIR = app.config.get('DWG_DIR')
TMP_DIR = app.config.get('TMP_DIR')
APP_NAME = app.config.get('APP_NAME')
WEB_NAME = app.config.get('WEB_NAME')
RANGE = app.config.get('RANGE')


def getdir(dir=DWG_DIR):
    dirlist_out = []
    dirlist = os.listdir(dir)
    for dir in dirlist:
        if os.path.isdir(DWG_DIR + '/' + dir):
            dirlist_out.append(dir)
    return dirlist_out


def getfile(dir=DWG_DIR):
    filelist_out = []
    filelist = os.listdir(dir)
    for file in filelist:
        if os.path.isfile(dir + '/' + file):
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
    filelist = getfile(DWG_DIR + '/' + dir_cu)
    page = getpage(filelist, page_cu)
    args = dict()
    args['app_name'] = APP_NAME
    args['web_name'] = WEB_NAME
    args['dirlist'] = dirlist
    args['filelist'] = filelist
    args['dir_cu'] = dir_cu
    args['page_cu'] = page_cu
    args['page'] = page
    return render_template('index.html', args=args)


@app.route('/show/<dir>/<filename>')
def show(dir, filename):
    if re.search(r'\.d[wx][gft]$', filename, re.M | re.I):
        return redirect(url_for('showdwg', dir=dir, filename=filename))
    elif re.search(r'\.pdf$', filename, re.I):
        return redirect(url_for('showpdf', dir=dir, filename=filename))
    else:
        flash('无法打开 "' + filename + '"，暂未支持该文件格式。')
        return redirect(url_for('index', dir_cu=dir, page_cu=1))


@app.route('/showdwg/<dir>/<filename>')
def showdwg(dir, filename):
    args = dict()
    source = DWG_DIR + '/' + dir + '/' + filename
    dest = TMP_DIR + '/' + request.remote_addr.replace('.', '-')
    shutil.copy(source, './static/' + dest)
    url = url_for('static', filename=dest, _external=True)
    args['filename'] = filename
    args['url'] = url
    return render_template('showdwg.html', args=args)


@app.route('/showpdf/<dir>/<filename>')
def showpdf(dir, filename):
    args = dict()
    source = DWG_DIR + '/' + dir + '/' + filename
    dest = TMP_DIR + '/' + request.remote_addr.replace('.', '-') + '.pdf'
    shutil.copy(source, './static/' + dest)
    url = url_for('static', filename=dest, _external=True)
    args['filename'] = filename
    args['url'] = url
    return render_template('showpdf.html', args=args)


@app.route('/about')
def about():
    dirlist = getdir()
    args = dict()
    args['dirlist'] = dirlist
    args['app_name'] = APP_NAME
    args['web_name'] = WEB_NAME
    return render_template('about.html', args=args)


@app.route('/login')
def login():
    args = dict()
    args['app_name'] = APP_NAME
    args['web_name'] = WEB_NAME
    args['debug'] = app.config['DEBUG']
    return render_template('login.html', args=args)


@app.route('/signup')
def signup():
    pass
