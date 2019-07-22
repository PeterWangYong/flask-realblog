#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wangyong
# @Time    : 2019/5/9 下午12:42
# @File    : __init__.py.py

import os
import click
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFError
from flask_sqlalchemy import get_debug_queries
from flask_login import current_user
from realblog.web.blog import web_blog_bp
from realblog.web.admin import web_admin_bp

from realblog.libs.extensions import db, bootstrap, login_manager, csrf, ckeditor, mail, moment, migrate
from realblog.models.blog import Post, Category, Comment
from realblog.models.admin import Admin
from realblog.setting import setting
from realblog.secure import secure

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV')

    # 这里硬编码模块名或者包名的原因是希望在其他地方创建app也能够成功运行
    # 这里的名字如果写错就会导致static和templates文件找不到的错误
    app = Flask('realblog')
    app.config.from_object(setting[config_name])
    app.config.from_object(secure[config_name])

    register_blueprints(app)
    register_extensions(app)
    register_logging(app)
    register_commands(app)
    register_error_handlers(app)
    register_shell_context(app)
    register_template_context(app)
    register_request_handlers(app)

    return app


def register_blueprints(app):
    app.register_blueprint(web_blog_bp)
    app.register_blueprint(web_admin_bp)


def register_extensions(app):
    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    migrate.init_app(app)


def register_logging(app):
    class RequestFormatter(logging.Formatter):

        # 重写format方法添加自定义属性，format方法用于转换日志对象为格式化字符串
        # 实际上通过self._fmt % record.__dict__完成格式化
        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super().format(record)

    request_formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )

    # 设置文件回滚日志
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = RotatingFileHandler(os.path.join(basedir, 'logs/realblog.log'), maxBytes=10 * 1024 * 1024, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # 发送日志邮件
    mail_handler = SMTPHandler(
        mailhost=app.config['MAIL_SERVER'],
        fromaddr=app.config['MAIL_USERNAME'],
        toaddrs=['ADMIN_EMAIL'],
        subject='Realblog Application Error',
        credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
    )

    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(request_formatter)

    # 在开发环境下关闭日志记录
    if not app.debug:
        app.logger.addHandler(mail_handler)
        app.logger.addHandler(file_handler)


# 注册python shell上下文管理器(函数),当执行flask shell时所有的函数都会自动执行，返回一个字典
# 字典中的对象可以在flask shell中直接调用
def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, Post=Post, Category=Category)


# 注册模版上下文，返回一个字典
# 字典中的对象可以在模版中直接调用
def register_template_context(app):
    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        # 注册全局的categories用于分类展示，因为分类在所有页面传入都一样
        categories = Category.query.order_by(Category.name).all()
        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None
        return dict(
            admin=admin,
            categories=categories,
            unread_comments=unread_comments
        )


# 注册错误处理器，接收状态码或者异常类
def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', descrption=e), 400


# 注册flask命令，可以直接在命令行调用  flask <command> <options>
def register_commands(app):

    # 初始化数据库
    # click库用于构建命令行工具
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='create after drop.')
    def initdb(drop):
        if drop:
            # abort=True 表示当输入值不符合要求时会终止执行
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    # 初始化项目
    @app.cli.command()
    @click.option('--username', prompt=True, help='The username used to login.')
    @click.option('--password', prompt=True, hide_input=True,
                  confirmation_prompt=True, help='The password used to login.')
    def init(username, password):
        """Building RealLog, just for you."""

        click.echo('Initializing the database...')
        db.create_all()

        with db.auto_commit():
            admin = Admin.query.first()
            if admin is not None:
                click.echo('The administrator already exists, updating...')
                admin.username = username
                admin.password = password
            else:
                click.echo('Creating the temporary administrator account...')
                admin = Admin(
                    username=username,
                    password=password,
                    blog_title='RealBlog',
                    blog_sub_title='Just Blog for Real',
                    name='peter',
                    about='i am handsome'
                )
                db.session.add(admin)

            category = Category.query.first()
            if category is None:
                click.echo('Creating the default category...')
                category = Category(name='Default')
                db.session.add(category)
        click.echo('Done.')

    # 创建假数据
    @app.cli.command()
    @click.option('--category', default=10, help='Quantity of categories, default is 10.')
    @click.option('--post', default=50, help='Quantity of posts, default is 50.')
    @click.option('--comment', default=500, help='Quantity of comments, default is 500.')
    def forge(category, post, comment):
        from realblog.libs.fakes import fake_categories, fake_posts, fake_admin, fake_comments
        db.drop_all()
        db.create_all()
        click.echo('Generating the administrator...')
        fake_admin()
        click.echo("Generating {} categories...".format(category))
        fake_categories(category)
        click.echo("Generating {} posts...".format(post))
        fake_posts(post)
        click.echo("Generating {} comments...".format(comment))
        fake_comments(comment)
        click.echo('Done.')


# 注册请求钩子函数
def register_request_handlers(app):
    # 开发模式下SQLAlchemy会记录每一次请求的所有SQL查询，我们可以进行性能分析
    @app.after_request
    def query_profiler(response):
        for q in get_debug_queries():
            if q.duration >= app.config['SQL_SLOW_QUERY_THRESHOLD']:
                app.logger.warning('Slow query: Duration: {}\n Context: {}\nQuery: {}\n '.format(
                    q.duration, q.context, q.statement))
        return response
