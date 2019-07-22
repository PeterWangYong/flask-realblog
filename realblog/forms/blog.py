#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wangyong
# @Time    : 2019/5/10 下午12:18
# @File    : blog.py

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, ValidationError, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length, Optional, URL, Email
from flask_ckeditor import CKEditorField
from realblog.models.blog import Category


class PostForm(FlaskForm):
    title = StringField('title', validators=[DataRequired(), Length(1, 60)])
    # coerce 提供一个函数接受浏览器返回的字符串进行类型转换
    category = SelectField('Category', coerce=int, default=1)
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        # super(PostForm, self)
        super().__init__(*args, **kwargs)
        # Flask-SQLAlchemy 需要在应用上下文才能调用，获得数据库配置信息
        # category.id 是存储的值, category.name 是显示的名称
        self.category.choices = [(category.id, category.name) for category in Category.query.order_by(Category.name).all()]


class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    submit = SubmitField()

    def validate_name(self, field):
        if Category.query.filter_by(name=field.data).first():
            raise ValidationError('Name already in use.')


class CommentForm(FlaskForm):
    author = StringField('姓名', validators=[DataRequired(), Length(1, 30)])
    email = StringField('邮箱', validators=[DataRequired(), Email(), Length(1, 254)])
    body = TextAreaField('评论', validators=[DataRequired()])
    submit = SubmitField()


class AdminCommentForm(CommentForm):
    author = HiddenField()
    email = HiddenField()
