#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wangyong
# @Time    : 2019/5/9 下午1:08
# @File    : extensions.py

from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy
from contextlib import contextmanager
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_moment import Moment
from flask_wtf import CSRFProtect
from flask_ckeditor import CKEditor
from flask_mail import Mail
from flask_migrate import Migrate


# 实现自动提交回滚
class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            print(e)


db = SQLAlchemy()
bootstrap = Bootstrap()
login_manager = LoginManager()
moment = Moment()
csrf = CSRFProtect()
ckeditor = CKEditor()
mail = Mail()
migrate = Migrate()


# 根据cookies中存储的user_id获取用户对象，提供给current_user
@login_manager.user_loader
def load_user(user_id):
    from realblog.models.admin import Admin
    user = Admin.query.get(int(user_id))
    return user
