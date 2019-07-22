#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wangyong
# @Time    : 2019/5/9 下午2:02
# @File    : base.py

from datetime import datetime
from realblog.libs.extensions import db


class Base(db.Model):
    __abstract__ = True
    create_time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    status = db.Column(db.SmallInteger, default=1)

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(key, attrs_dict) and key != 'id':
                setattr(self, key, value)


