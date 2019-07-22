#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wangyong
# @Time    : 2019/5/9 下午1:08
# @File    : setting.py


class BaseSetting:
    SQL_SLOW_QUERY_THRESHOLD = 1
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POST_PER_PAGE = 10
    MANAGE_POST_PER_PAGE = 15
    COMMENT_PER_PAGE = 15
    BLUELOG_EMAIL = 'admin@admin.com'


class DevelopmentSetting(BaseSetting):
    pass


class ProductionSetting(BaseSetting):
    pass


setting = {
    'development': DevelopmentSetting,
    'production': ProductionSetting
}
