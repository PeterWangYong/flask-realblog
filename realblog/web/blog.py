#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wangyong
# @Time    : 2019/5/9 下午1:40
# @File    : blog.py

from flask.blueprints import Blueprint
from flask import current_app, request, render_template, url_for, flash, redirect

from realblog.forms.blog import AdminCommentForm, CommentForm
from realblog.models.blog import Category, Post, Comment
from flask_login import current_user
from realblog.libs.extensions import db

web_blog_bp = Blueprint('web_blog', __name__)


@web_blog_bp.route('/')
def index():
    # type=int用于校验和转换传入参数，如果参数错误则使用默认值1
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['POST_PER_PAGE']
    # 分页获取文章记录.paginate
    # pagination 分页对象
    pagination = Post.query.order_by(Post.create_time.desc()).paginate(page, per_page)
    # 当前页数的记录列表
    posts = pagination.items
    return render_template('blog/index.html', pagination=pagination, posts=posts)


@web_blog_bp.route('/category/<int:category_id>')
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['POST_PER_PAGE']
    # with_parent传入.relationship定义的关系属性
    pagination = Post.query.with_parent(category).order_by(Post.create_time.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('blog/category.html', category=category, pagination=pagination, posts=posts)


@web_blog_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['COMMENT_PER_PAGE']
    pagination = Comment.query.with_parent(post).filter_by(reviewed=True).order_by(Comment.create_time.asc()).paginate(
        page, per_page)
    comments = pagination.items

    # 区分管理员评论和匿名用户评论
    if current_user.is_authenticated:
        form = AdminCommentForm()
        form.author.data = current_user.name
        form.email.data = current_app.config['BLUELOG_EMAIL']
        from_admin = True
        reviewed = True
    else:
        form = CommentForm()
        from_admin = False
        reviewed = False

    if form.validate_on_submit():
        with db.auto_commit():
            author = form.author.data
            email = form.email.data
            body = form.body.data
            comment = Comment(
                author=author, email=email, body=body,
                from_admin=from_admin, post=post, reviewed=reviewed)
            replied_id = request.args.get('reply')
            if replied_id:
                replied_comment = Comment.query.get_or_404(replied_id)
                comment.replied = replied_comment
                # send_new_reply_email(replied_comment)
            db.session.add(comment)
        if current_user.is_authenticated:  # send message based on authentication status
            flash('Comment published.', 'success')
        else:
            flash('Thanks, your comment will be published after reviewed.', 'info')
            # send_new_comment_email(post)  # send notification email to admin
        return redirect(url_for('web_blog.show_post', post_id=post_id))
    return render_template('blog/post_detail.html', post=post, pagination=pagination, form=form, comments=comments)


@web_blog_bp.route('/reply/comment/<int:comment_id>')
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if not comment.post.can_comment:
        flash('评论已被关闭', 'warning')
        return redirect(url_for('web_blog.show_post', post_id=comment.post.id))
    return redirect(
        url_for('web_blog.show_post', post_id=comment.post_id, reply=comment_id, author=comment.author) + '#comment-form')


@web_blog_bp.route('/about')
def about():
    return render_template('blog/about.html')
