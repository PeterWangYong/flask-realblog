#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wangyong
# @Time    : 2019/5/13 下午7:54
# @File    : admin.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length
from flask_ckeditor import CKEditorField


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('密码', validators=[DataRequired(), Length(1, 128)])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')


class SettingForm(FlaskForm):
    name = StringField('姓名', validators=[DataRequired(), Length(1, 70)])
    blog_title = StringField('博客标题', validators=[DataRequired(), Length(1, 60)])
    blog_sub_title = StringField('博客子标题', validators=[DataRequired(), Length(1, 100)])
    about = CKEditorField('自我介绍', validators=[DataRequired()])
    submit = SubmitField()