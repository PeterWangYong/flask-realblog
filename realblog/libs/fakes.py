#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wangyong
# @Time    : 2019/5/9 下午1:09
# @File    : fakes.py

import random
from faker import Faker
from realblog.models.blog import Category, Post, Comment
from realblog.models.admin import Admin
from realblog.libs.extensions import db

fake = Faker()


def fake_admin():
    with db.auto_commit():
        admin = Admin(
            username='admin',
            password='admin',
            blog_title='RealBlog',
            blog_sub_title='Just Blog for Real',
            name='peter',
            about='i am handsome'
        )
        db.session.add(admin)


def fake_categories(count=10):
    with db.auto_commit():
        category = Category(name='Default')
        db.session.add(category)

        for i in range(count):
            category = Category(name=fake.word())
            db.session.add(category)


def fake_posts(count=50):
    with db.auto_commit():
        for i in range(count):
            post = Post(
                title=fake.sentence(),
                body=fake.text(2000),
                category=Category.query.get(random.randint(1, Category.query.count())),
                create_time=fake.date_time_this_year()
            )
            db.session.add(post)


def fake_comments(count=500):
    salt = int(count * 0.1)
    with db.auto_commit():
        # 审核通过的评论
        for i in range(count):
            comment = Comment(
                author=fake.name(),
                email=fake.email(),
                body=fake.sentence(),
                create_time=fake.date_time_this_year(),
                reviewed=True,
                post=Post.query.get(random.randint(1, Post.query.count()))
            )
            db.session.add(comment)

        # 10%未审核的评论
        for i in range(salt):
            comment = Comment(
                author=fake.name(),
                email=fake.email(),
                body=fake.sentence(),
                create_time=fake.date_time_this_year(),
                reviewed=False,
                post=Post.query.get(random.randint(1, Post.query.count()))
            )
            db.session.add(comment)
        # 来自admin的评论
        comment = Comment(
            author='Peter',
            email='admin@admin.com',
            body=fake.sentence(),
            create_time=fake.date_time_this_year(),
            from_admin=True,
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

        # 10%的回复
    with db.auto_commit():
        for i in range(salt):
            comment = Comment(
                author=fake.name(),
                email=fake.email(),
                body=fake.sentence(),
                create_time=fake.date_time_this_year(),
                reviewed=True,
                replied=Comment.query.get(random.randint(1, Comment.query.count())),
                post=Post.query.get(random.randint(1, Post.query.count()))
            )
            db.session.add(comment)
