#!/usr/bin/env python3
# coding:utf-8

from myapp import app


if __name__ == '__main__':
    app.run(host=app.config.get('HOST'))
