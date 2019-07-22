#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wangyong
# @Time    : 2019/5/14 上午8:37
# @File    : utils.py

from urllib.parse import urlparse, urljoin
from flask import request, redirect, url_for, current_app


# 校验url是否是本地url，在回跳时防止篡改
def is_safe_url(target):
    # 获取主机url
    ref_url = urlparse(request.host_url)
    # urljoin将校验target，如果target不存在主机url部分，则添加为host_url
    # 有时候我们判断target.startswith('/')，但无法兼顾完整url的情况
    # 本质上就是要校验host_url是否相同
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


# 回跳到请求地址
# redirect_back用于本页面的请求比如button点击后仍停留在本页面或者登录后跳回原页面等
def redirect_back(default='web_blog.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if target and is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))
