#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wangyong
# @Time    : 2019/5/9 下午1:58
# @File    : blog.py

from realblog.libs.extensions import db
from realblog.models.base import Base


class Category(Base):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    posts = db.relationship('Post', back_populates='category')


class Post(Base):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(60), nullable=False)
    body = db.Column(db.Text)
    can_comment = db.Column(db.Boolean, default=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', back_populates='posts')
    comments = db.relationship('Comment', back_populates='post', cascade='all,delete-orphan')


class Comment(Base):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author = db.Column(db.String(30))
    email = db.Column(db.String(255))
    body = db.Column(db.Text)
    from_admin = db.Column(db.Boolean, default=False)
    # 评论是否通过审核
    reviewed = db.Column(db.Boolean, default=False)
    # 定义评论和文章的关系
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', back_populates='comments')
    # 回复本身也是评论，使用邻接列表关系来描述
    # cascade（级连）当评论被删除时所有回复也会被删除
    # replies 是一的关系
    replies = db.relationship('Comment', back_populates='replied', cascade='all,delete-orphan')
    # remote_side 将id字段定义为关系的远端侧（即一对多中的一），replied_id就变为本地侧
    # 哪个关系定义了remote_side那么该关系为多的一侧（本地侧）
    # 邻接列表关系，设置一个指向自身的外键
    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])
