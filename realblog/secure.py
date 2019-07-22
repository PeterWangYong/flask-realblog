#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wangyong
# @Time    : 2019/5/9 下午1:15
# @File    : secure.py


class BaseSecure:
    SECRET_KEY = "jiefliefknfijefiekfjefjiefiejfieif"

    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'xxxxxxxxxxxxx'
    MAIL_PASSWORD = 'xxxxxxxxxxxx'
    MAIL_DEFAULT_SENDER = ('Realblog', MAIL_USERNAME)


class DevelopmentSecure(BaseSecure):

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost:3306/realblog'


class ProductionSecure(BaseSecure):
    pass


secure = {
    'development': DevelopmentSecure,
    'production': ProductionSecure
}
