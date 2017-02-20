#!/usr/bin/env python3
# coding:utf-8

from myapp import app

HOST = app.config.get('HOST')

if __name__ == '__main__':
    app.run(host=HOST)
