# -*- coding: utf-8 -*-
"""
	:author: Grey Li (李辉)
	:url: http://greyli.com
	:copyright: © 2018 Grey Li <withlihui@gmail.com>
	:license: MIT, see LICENSE for more details.
"""
import os
import time

from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint, send_from_directory, Response
from flask_login import login_required, current_user
from flask_ckeditor import upload_success, upload_fail

from bluelog.extensions import db
from bluelog.forms import SettingForm, PostForm, CategoryForm, LinkForm
from bluelog.models import Post, Category, Comment, Link
from bluelog.utils import redirect_back, allowed_file

from bluelog.MzUtils import backup_zip, compress_image, ip2location
from bluelog.log import MzLog

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
	form = SettingForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.blog_title = form.blog_title.data
		current_user.blog_sub_title = form.blog_sub_title.data
		current_user.about = form.about.data
		db.session.commit()
		flash('Setting updated.', 'success')
		return redirect(url_for('blog.index'))
	form.name.data = current_user.name
	form.blog_title.data = current_user.blog_title
	form.blog_sub_title.data = current_user.blog_sub_title
	form.about.data = current_user.about
	return render_template('admin/settings.html', form=form)
	
# 数据统计页面
# 暂时先这么写，不太好弄
@admin_bp.route('/statistics')
def statistics():
	# 统计总字数
	posts = Post.query.all()
	all_view_count = MzLog.get_all_view_count()
	# 获取最近的访问记录
	page = int(request.args.get("page", 0)) if int(request.args.get("page", 0)) >= 0 else 0
	records = MzLog.get_records(
		n=10,
		offset=page*10
		)
	return render_template('admin/statistics.html', 
		posts=posts, all_view_count=all_view_count, records=records,
		ip2location=ip2location, page=page)
	
# 备份功能
@admin_bp.route('/backup')
@login_required
def backup_data():
	# 打包
	backup_zip(
		upload_dir = current_app.config['BLUELOG_UPLOAD_PATH'],
		db_file = current_app.config['BLUELOG_UPLOAD_PATH'] + '/../data-dev.db',
		backup_file = current_app.config['BLUELOG_UPLOAD_PATH'] + '/../bak.zip'
	)
	return send_from_directory(current_app.config['BLUELOG_UPLOAD_PATH']+'/..', 'bak.zip')

# ip属地接口，直接返回字符串
@admin_bp.route('/ip_query/<ip>')
@login_required
def ip_query(ip):
	return ip2location(ip)


@admin_bp.route('/post/manage')
@login_required
def manage_post():
	page = request.args.get('page', 1, type=int)
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
		page=page, per_page=current_app.config['BLUELOG_MANAGE_POST_PER_PAGE'])
	posts = pagination.items
	return render_template('admin/manage_post.html', page=page, pagination=pagination, posts=posts)


@admin_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		title = form.title.data
		body = form.body.data
		category = Category.query.get(form.category.data)
		post = Post(title=title, body=body, category=category)
		# same with:
		# category_id = form.category.data
		# post = Post(title=title, body=body, category_id=category_id)
		db.session.add(post)
		db.session.commit()
		# Submit直接返回，save的话跳到edit的编辑页面
		if form.save.data == True:
			# save
			flash('Post saved.', 'success')   # 跳转到编辑页面
			return redirect(url_for('admin.edit_post', post_id=post.id))
		elif form.submit.data == True:
			flash('Post created.', 'success')
			return redirect(url_for('blog.show_post', post_id=post.id))
	return render_template('admin/new_post.html', form=form)


@admin_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
	form = PostForm()
	post = Post.query.get_or_404(post_id)
	if form.validate_on_submit():
		post.title = form.title.data
		post.body = form.body.data
		post.category = Category.query.get(form.category.data)
		db.session.commit()
		# Submit直接返回，Save的话跳到编辑页面
		# print(form.save.data)   # True or False
		if form.save.data == True:
			# save
			flash('Post saved.', 'success') # 跟着最下面返回
		elif form.submit.data == True:
			flash('Post updated.', 'success')
			return redirect(url_for('blog.show_post', post_id=post.id))
	form.title.data = post.title
	form.body.data = post.body
	form.category.data = post.category_id
	return render_template('admin/edit_post.html', form=form)


@admin_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	db.session.delete(post)
	db.session.commit()
	flash('Post deleted.', 'success')
	return redirect_back()

@admin_bp.route('/post/<int:post_id>/set-hidden', methods=['POST'])
@login_required
def set_hidden(post_id):
	post = Post.query.get_or_404(post_id)
	if post.hidden:
		post.hidden = False
		flash('Set post unhidden.', 'success')
	else:
		post.hidden = True
		flash('Set post hidden.', 'success')
	db.session.commit()
	return redirect_back()

@admin_bp.route('/post/<int:post_id>/set-comment', methods=['POST'])
@login_required
def set_comment(post_id):
	post = Post.query.get_or_404(post_id)
	if post.can_comment:
		post.can_comment = False
		flash('Comment disabled.', 'success')
	else:
		post.can_comment = True
		flash('Comment enabled.', 'success')
	db.session.commit()
	return redirect_back()


@admin_bp.route('/comment/manage')
@login_required
def manage_comment():
	filter_rule = request.args.get('filter', 'all')  # 'all', 'unreviewed', 'admin'
	page = request.args.get('page', 1, type=int)
	per_page = current_app.config['BLUELOG_COMMENT_PER_PAGE']
	if filter_rule == 'unread':
		filtered_comments = Comment.query.filter_by(reviewed=False)
	elif filter_rule == 'admin':
		filtered_comments = Comment.query.filter_by(from_admin=True)
	else:
		filtered_comments = Comment.query

	pagination = filtered_comments.order_by(Comment.timestamp.desc()).paginate(page=page, per_page=per_page)
	comments = pagination.items
	return render_template('admin/manage_comment.html', comments=comments, pagination=pagination)


@admin_bp.route('/comment/<int:comment_id>/approve', methods=['POST'])
@login_required
def approve_comment(comment_id):
	comment = Comment.query.get_or_404(comment_id)
	comment.reviewed = True
	db.session.commit()
	flash('Comment published.', 'success')
	return redirect_back()


@admin_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
	comment = Comment.query.get_or_404(comment_id)
	db.session.delete(comment)
	db.session.commit()
	flash('Comment deleted.', 'success')
	return redirect_back()


@admin_bp.route('/category/manage')
@login_required
def manage_category():
	return render_template('admin/manage_category.html')


@admin_bp.route('/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
	form = CategoryForm()
	if form.validate_on_submit():
		name = form.name.data
		category = Category(name=name)
		db.session.add(category)
		db.session.commit()
		flash('Category created.', 'success')
		return redirect(url_for('.manage_category'))
	return render_template('admin/new_category.html', form=form)


@admin_bp.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
	form = CategoryForm()
	category = Category.query.get_or_404(category_id)
	if category.id == 1:
		flash('You can not edit the default category.', 'warning')
		return redirect(url_for('blog.index'))
	if form.validate_on_submit():
		category.name = form.name.data
		db.session.commit()
		flash('Category updated.', 'success')
		return redirect(url_for('.manage_category'))

	form.name.data = category.name
	return render_template('admin/edit_category.html', form=form)


@admin_bp.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
	category = Category.query.get_or_404(category_id)
	if category.id == 1:
		flash('You can not delete the default category.', 'warning')
		return redirect(url_for('blog.index'))
	category.delete()
	flash('Category deleted.', 'success')
	return redirect(url_for('.manage_category'))


@admin_bp.route('/link/manage')
@login_required
def manage_link():
	return render_template('admin/manage_link.html')


@admin_bp.route('/link/new', methods=['GET', 'POST'])
@login_required
def new_link():
	form = LinkForm()
	if form.validate_on_submit():
		name = form.name.data
		url = form.url.data
		link = Link(name=name, url=url)
		db.session.add(link)
		db.session.commit()
		flash('Link created.', 'success')
		return redirect(url_for('.manage_link'))
	return render_template('admin/new_link.html', form=form)


@admin_bp.route('/link/<int:link_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_link(link_id):
	form = LinkForm()
	link = Link.query.get_or_404(link_id)
	if form.validate_on_submit():
		link.name = form.name.data
		link.url = form.url.data
		db.session.commit()
		flash('Link updated.', 'success')
		return redirect(url_for('.manage_link'))
	form.name.data = link.name
	form.url.data = link.url
	return render_template('admin/edit_link.html', form=form)


@admin_bp.route('/link/<int:link_id>/delete', methods=['POST'])
@login_required
def delete_link(link_id):
	link = Link.query.get_or_404(link_id)
	db.session.delete(link)
	db.session.commit()
	flash('Link deleted.', 'success')
	return redirect(url_for('.manage_link'))


@admin_bp.route('/uploads/<path:filename>')
def get_image(filename):
	# return send_from_directory(current_app.config['BLUELOG_UPLOAD_PATH'], filename)   # 旧版本直接返回文件
	# 检查安全性
	if '..' in filename:
		return ''
	# 拼接路径
	fpath = os.path.join(current_app.config['BLUELOG_UPLOAD_PATH'], filename)
	print(fpath)
	img = compress_image(fpath)   # 对文件大小进行压缩 默认压到500kb以下
	return Response(img, mimetype="image/jpeg")


# 登录后才能上传
@admin_bp.route('/upload', methods=['POST'])
@login_required
def upload_image():
	f = request.files.get('upload')
	if not allowed_file(f.filename):
		return upload_fail('Image only!')
	# 这里需要对文件名进行重新处理，转化成时间戳+后缀名的格式
	_ext = f.filename.rsplit('.', 1)[1].lower()   # 取后缀名
	_fname = str(int(time.time())) + '.' + _ext    # 拼接新的文件名
	f.save(os.path.join(current_app.config['BLUELOG_UPLOAD_PATH'], _fname))
	url = url_for('.get_image', filename=_fname)
	return upload_success(url, _fname)
