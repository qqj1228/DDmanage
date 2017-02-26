#!/usr/bin/env python3
# coding:utf-8

from flask import jsonify
from . import app

# 该组APIError用于处理API调用后不符合应用逻辑的异常，需要传递到客户端处
# 故没有设置HTTP状态码，Flask会默认为200，如果加了自定义HTTP状态码的话
# Flask就会返回出错状态，错误信息无法传递到客户端处

class APIError(Exception):
    '''
    The base APIError class  which contains error(required), data(optional)
    and message(optional).
    '''
    def __init__(self, error, data='', message=''):
        super().__init__(message)
        self.error = error
        self.data = data
        self.message = message

    def to_dict(self):
        rv = dict()
        rv['error'] = self.error
        rv['data'] = self.data
        rv['message'] = self.message
        return rv


class APIValueError(APIError):
    '''
    Indicate the input value has error or invalid.
    The data specifies the error field of input form.
    '''
    def __init__(self, field, message=''):
        super().__init__('value:invalid', field, message)


class APIResourceNotFoundError(APIError):
    '''
    Indicate the resource was not found.
    The data specifies the resource name.
    '''
    def __init__(self, field, message=''):
        super().__init__('value:notfound', field, message)


class APIPermissionError(APIError):
    '''
    Indicate the api has no permission.
    '''
    def __init__(self, message=''):
        super().__init__('permission:forbidden', 'permission', message)


@app.errorhandler(APIError)
def handle_api_error(error):
    response = jsonify(error.to_dict())
    return response


@app.errorhandler(APIValueError)
def handle_api_value_error(error):
    response = jsonify(error.to_dict())
    return response


@app.errorhandler(APIResourceNotFoundError)
def handle_api_resource_not_found_error(error):
    response = jsonify(error.to_dict())
    return response


@app.errorhandler(APIPermissionError)
def handle_api_permission_error(error):
    response = jsonify(error.to_dict())
    return response
