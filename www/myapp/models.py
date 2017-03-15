# coding:utf-8

import os
from datetime import datetime

from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from . import db, login_manager


@login_manager.user_loader
# 传入的user_id参数是unicode字符串
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    dwgrecords = db.relationship('DwgRecord', backref='user_r', lazy='dynamic')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if current_app.config['TESTING']:
            self.name = 'test'
            self.email = 'test@test.com'
        if self.email == current_app.config['EMAIL_ADMIN']:
            self.role_r = Role.query.filter_by(permission=0xff).first()
            dir = self.email
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], dir)
            if not os.path.isdir(path):
                os.mkdir(path)
        else:
            self.role_r = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_forgot_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'forget': self.id})

    def verify_forgot_token(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('forget') != self.id:
            return False
        return True

    def can(self, permission):
        return (self.role_r.permission & permission) == permission

    def is_admin(self):
        return self.can(Permission.ADMIN)

    def to_json(self):
        json_user = {
            'name': self.name,
            'email': self.email,
            'role_name': self.role_r.name
        }
        return json_user

    def __repr__(self):
        return 'User-%r' % self.name


class Permission:
    DEFAULT = 0x00
    DWG_BROWSE = 0x01
    DWG_UPDOWN = 0x02
    FILE_BROWSE = 0x04
    FILE_UPDOWN = 0x08
    ADMIN = 0x80


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permission = db.Column(db.Integer)
    users = db.relationship('User', backref='role_r', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            '默认用户': (Permission.DEFAULT, True),
            '普通用户': (Permission.DWG_BROWSE | Permission.FILE_BROWSE | Permission.FILE_UPDOWN, False),
            '图纸管理员': (Permission.DWG_BROWSE | Permission.DWG_UPDOWN | Permission.FILE_BROWSE | Permission.FILE_UPDOWN, False),
            '系统管理员': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permission = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def to_json(self):
        json_role = {
            'name': self.name
        }
        return json_role

    def __repr__(self):
        return 'Role-%r' % self.name


class DwgRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dwg = db.Column(db.String(128), nullable=False)
    url = db.Column(db.String(128), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.datetime = datetime.now()

    def to_json(self):
        json_dwgrecord = {
            'user': self.user_r.name,
            'dwg': self.dwg,
            'url': self.url,
            'datetime': self.datetime
        }
        return json_dwgrecord

    def __repr__(self):
        return 'DwgRecord-%r' % self.dwg
