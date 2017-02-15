#!/usr/bin/env python3
# coding:utf-8

import logging
import os
from flask import Flask
from flask import render_template

# 定义配置项
DEBUG = True
DWG_DIR = '/users/dwg'
NAME = '图纸管理程'
RANGE = 3

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


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
    args['web_name'] = NAME
    args['dirlist'] = dirlist
    args['filelist'] = filelist
    args['dir_cu'] = dir_cu
    args['page_cu'] = page_cu
    args['page'] = page
    return render_template('index.html', args=args)


@app.route('/hello')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=DEBUG)
