#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wangyong
# @Time    : 2019/5/14 上午8:22
# @File    : admin.py

from flask import Blueprint, redirect, url_for, request, flash, render_template, current_app
from flask_login import current_user, login_user, login_required, logout_user

from realblog.libs.utils import redirect_back
from realblog.models.admin import Admin
from realblog.models.blog import Post, Category, Comment
from realblog.forms.admin import LoginForm, SettingForm
from realblog.forms.blog import PostForm, CategoryForm
from realblog.libs.extensions import db

web_admin_bp = Blueprint('web_admin', __name__)


# 登录登出
@web_admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('web_blog.index'))

    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and admin.check_password(form.password.data):
            login_user(admin, form.remember.data)
            # flash传入元组的分类消息，前者为内容，后者为样式字符，模版中使用with_categories=True调用
            flash('登录成功', 'info')
            return redirect_back()
        flash('Invalid username or password.', 'warning')
    return render_template('admin/login.html', form=form)


@web_admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('注销成功', 'info')
    return redirect(url_for('web_blog.index'))


# 博客配置
@web_admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingForm()
    if form.validate_on_submit():
        with db.auto_commit():
            current_user.name = form.name.data
            current_user.blog_title = form.blog_title.data
            current_user.blog_sub_title = form.blog_sub_title.data
            current_user.about = form.about.data
        flash('博客配置修改成功', 'success')
        return redirect(url_for('web_blog.index'))
    form.name.data = current_user.name
    form.blog_title.data = current_user.blog_title
    form.blog_sub_title.data = current_user.blog_sub_title
    form.about.data = current_user.about
    return render_template('admin/settings.html', form=form)


# 博客增删改
@web_admin_bp.route('/post/manage')
@login_required
def manage_post():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.create_time.desc()).paginate(
        page, per_page=current_app.config['MANAGE_POST_PER_PAGE']
    )
    posts = pagination.items
    return render_template('admin/manage_post.html', page=page, pagination=pagination, posts=posts)


@web_admin_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        with db.auto_commit():
            title = form.title.data
            body = form.body.data
            category = Category.query.get(form.category.data)
            post = Post(title=title, body=body, category=category)
            db.session.add(post)
        flash('文章创建成功', 'success')
        return redirect(url_for('web_blog.show_post', post_id=post.id))
    return render_template('admin/new_post.html', form=form)


@web_admin_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    if form.validate_on_submit():
        with db.auto_commit():
            post.title = form.title.data
            post.body = form.body.data
            post.category = Category.query.get(form.category.data)
        flash('文章更新成功', 'success')
        return redirect(url_for('web_blog.show_post', post_id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.category.data = post.category_id
    return render_template('admin/edit_post.html', form=form)


@web_admin_bp.route('/post/<int:post_id>/delete')
@login_required
def delete_post(post_id):
    with db.auto_commit():
        post = Post.query.get_or_404(post_id)
        db.session.delete(post)
    flash('文章删除成功', 'success')
    return redirect_back()


# 评论增删，管理审核
@web_admin_bp.route('/post/<int:post_id>/set-comment')
@login_required
def set_comment(post_id):
    """
    开启或关闭评论
    :param post_id:
    :return:
    """
    post = Post.query.get_or_404(post_id)
    with db.auto_commit():
        if post.can_comment:
            post.can_comment = False
            flash('评论已关闭', 'success')
        else:
            post.can_comment = True
            flash('评论已开启', 'success')
    return redirect_back()


@web_admin_bp.route('/comment/manage')
@login_required
def manage_comment():
    # 对评论添加过滤
    filter_rule = request.args.get('filter', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['COMMENT_PER_PAGE']
    if filter_rule == 'unread':
        filtered_comments = Comment.query.filter_by(reviewed=False)
    elif filter_rule == 'admin':
        filtered_comments = Comment.query.filter_by(from_admin=True)
    else:
        filtered_comments = Comment.query
    pagination = filtered_comments.order_by(Comment.create_time.desc()).paginate(page, per_page=per_page)
    comments = pagination.items
    return render_template('admin/manage_comment.html', comments=comments, pagination=pagination)


@web_admin_bp.route('/comment/<int:comment_id>/approve')
@login_required
def approve_comment(comment_id):
    with db.auto_commit():
        comment = Comment.query.get_or_404(comment_id)
        comment.reviewed = True
    flash('评论已公开', 'success')
    return redirect_back()


@web_admin_bp.route('/comment/<int:comment_id>/delete')
@login_required
def delete_comment(comment_id):
    with db.auto_commit():
        comment = Comment.query.get_or_404(comment_id)
        db.session.delete(comment)
    flash('评论已删除', 'success')
    return redirect_back()


# 分类增删改
@web_admin_bp.route('/category/manage')
@login_required
def manage_category():
    return render_template('admin/manage_category.html')


@web_admin_bp.route('/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        with db.auto_commit():
            name = form.name.data
            category = Category(name=name)
            db.session.add(category)
        flash('分类创建成功', 'success')
        return redirect(url_for('web_admin.manage_category'))
    return render_template('admin/new_category.html', form=form)


@web_admin_bp.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    form = CategoryForm()
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('你不能编辑默认类别', 'warning')
        return redirect(url_for('web_blog.index'))
    if form.validate_on_submit():
        with db.auto_commit():
            category.name = form.name.data
        flash('分类更新成功', 'success')
        return redirect(url_for('web_admin.manage_category'))
    form.name.data = category.name
    return render_template('admin/edit_category.html', form=form)


@web_admin_bp.route('/category/<int:category_id>/delete')
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('不能删除默认分类', 'warning')
        return redirect(url_for('web_blog.index'))
    category.delete()
    flash('分类已删除', 'success')
    return redirect(url_for('web_admin.manage_category'))

