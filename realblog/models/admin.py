#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wangyong
# @Time    : 2019/5/13 下午7:27
# @File    : admin.py

from realblog.libs.extensions import db
from realblog.models.base import Base
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Admin(Base, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False)
    _password_hash = db.Column('password', db.String(128), nullable=False)
    blog_title = db.Column(db.String(60), nullable=False)
    blog_sub_title = db.Column(db.String(100))
    name = db.Column(db.String(30))
    about = db.Column(db.Text)

    @property
    def password(self):
        return self._password_hash

    @password.setter
    def password(self, raw):
        self._password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self._password_hash, raw)
