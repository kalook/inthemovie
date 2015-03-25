# -*- coding: utf-8 -*-
from django.http import HttpResponse
import datetime
from libs.lib import *
from libs.api_request import *
from libs.digg_pagination import *
from django.http import HttpResponseRedirect
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from club.models import *
from member.models import *
import socket 
from django.core.paginator import Paginator, InvalidPage, EmptyPage
import os, os.path, sys
from datetime import datetime

def club_main(request):
	#기자단리뷰
	reporter_board = Boards.objects.get(code='reporter')
	reporter_posts = reporter_board.posts_set.order_by('-id')[:4]
	#영화리뷰
	movie_board = Boards.objects.get(code='movie')
	movie_posts = movie_board.posts_set.order_by('-id')[:4]	
	#공연리뷰
	performance_board = Boards.objects.get(code='performance')
	performance_posts = performance_board.posts_set.order_by('-id')[:4]
	#이러쿵저러쿵
	free_board = Boards.objects.get(code='free')
	free_posts = free_board.posts_set.order_by('-id')[:4]

	# 극장주변명소 attraction
	attraction_board = Boards.objects.get(code='attraction')
	attraction_posts = attraction_board.posts_set.order_by('-id')[:4]
	# 오프미팅 
	offmeeting_board = Boards.objects.get(code='offmeeting')
	offmeeting_posts = offmeeting_board.posts_set.order_by('-id')[:6]
	
	#지금 덕스클럽에서는
	now_ducksclub = Posts.objects.order_by('-reg_date')[:9]

	return render_to_response(
		'club/main.html',
		{
		'request' : request,
		'user' : request.user,
		'session' : request.session,
		'reporter_posts' : reporter_posts,
		'movie_posts' : movie_posts,
		'performance_posts' : performance_posts,
		'free_posts' : free_posts,
		'attraction_posts' : attraction_posts,		
		'offmeeting_posts' : offmeeting_posts,
		'now_ducksclub' : now_ducksclub,
		'main_banner' : get_main_banner(),
		'search_keyword' : get_search_keyword()
		}
	)
	
	
def club_list(request, code, page=1):
	board = Boards.objects.get(code=code)
	posts = board.posts_set.order_by('-id')
	paginator = Paginator(posts, 10)
	
	try:
		posts = paginator.page(page)
	except (EmptyPage, InvalidPage):
		posts = paginator.page(paginator.num_pages)
	
	digg = digg_pagination(paginator.page(page))
	
	request.session['current_page'] = page
	return render_to_response(
		'club/skin/'+board.type+'/list.html',
		{
		'request' : request,
		'user' : request.user,
		'session' : request.session,
		'code' : code,
		'board' : board,
		'posts' : posts,
		'page'  : page,
		'digg' : digg,
		'main_banner' : get_main_banner(),
		'search_keyword' : get_search_keyword()
		}
	)
	
def club_post_view(request, code, idx):

	board = Boards.objects.get(code=code)
	post = Posts.objects.get(id=idx)

	post.readed_count = post.readed_count + 1
	post.save()
	
	next_post = board.posts_set.order_by('id').filter(id__gt = idx)[:1]
	prev_post = board.posts_set.order_by('-id').filter(id__lt = idx)[:1]
	
	return render_to_response(
		'club/skin/'+board.type+'/view.html',
		{
			'request' : request,
			'user' : request.user,
			'session' : request.session,
			'code' : code,
			'board' : board,
			'post' : post,
			'next_post' : next_post,
			'prev_post' : prev_post,
			'main_banner' : get_main_banner(),
			'search_keyword' : get_search_keyword()
		}
	)

def handle_uploaded_file(f, code):
	upload_path = settings.STORAGE_PATH+'/'+code
	gen_name = GenPasswd()
	tmp_filename = (f.name).split('.')
	file_ext = tmp_filename[1]
	gen_file_name = datetime.now().strftime('%Y_%m_%d') + '_' + (gen_name) + '.' + file_ext
	if not os.path.exists(upload_path):
		os.makedirs(upload_path)	
	destination_path = upload_path+'/%s' % gen_file_name
	destination = open(destination_path, 'wb+')
	for chunk in f.chunks():
		destination.write(chunk)
	destination.close()
	return gen_file_name

def club_post(request, code):

	if ("user_id" not in request.session) or (request.session["user_id"] == ""):
		return HttpResponseRedirect('/login?url=' + request.get_full_path())

	board = Boards.objects.get(code=code)
	user_info = Users.objects.get(user_id=request.session['user_id'])
	errors = []

	if request.method == 'POST':
		thumnail = ''
		if 'thumnail' in request.FILES:
			thumnail = handle_uploaded_file(request.FILES['thumnail'], code)
		point = Posts.objects.create(
			board = board,
			user = user_info,
			title = request.POST['title'],
			content = request.POST['ir1'],
			ip = request.META['REMOTE_ADDR'],
			thumnail = thumnail
		)
		return HttpResponseRedirect('/club/'+code+'/')
	
	return render_to_response(
		'club/skin/'+board.type+'/post.html',
		{
			'request' : request,
			'user' : request.user,
			'session' : request.session,
			'code' : code,
			'board' : board,
			'errors' : errors,
			'main_banner' : get_main_banner(),
			'search_keyword' : get_search_keyword()
		}
	)
	
def club_post_edit(request, code, idx):
	board = Boards.objects.get(code=code)
	post = Posts.objects.get(id=idx)
	if request.method == 'POST':
		if 'is_del' in request.POST:
			if request.FILES['thumnail']:
				thumnail = handle_uploaded_file(request.FILES['thumnail'], code)
				post.thumnail	= thumnail
		post.title		= request.POST['title']
		post.content	= request.POST['ir1']
		post.save()
		return HttpResponseRedirect('/club/'+code+'/post/'+idx)

	return render_to_response(
		'club/skin/'+board.type+'/edit.html',
		{
			'request' : request,
			'user' : request.user,
			'session' : request.session,
			'code' : code,
			'board' : board,
			'post' : post,
			'main_banner' : get_main_banner(),
			'search_keyword' : get_search_keyword()
		}
	)

def club_post_delete(request, code, idx):
	board = Boards.objects.get(code=code)
	post = Posts.objects.get(id=idx)
	if post.user.user_id == request.session['user_id']:
		post.delete()
		return HttpResponseRedirect('/club/'+code+'/')
	else:
		return HttpResponse('false', mimetype="text/html")

def club_comment_post(request):
	if request.is_ajax():
		board = Boards.objects.get(code=request.POST['code'])
		post = Posts.objects.get(id=request.POST['idx'])
		user_info = Users.objects.get(user_id=request.session['user_id'])
		comment = Comments.objects.create(
			board = board,
			post = post,
			user = user_info,
			comment = request.POST['content'],
			ip = request.META['REMOTE_ADDR']
		)
	return HttpResponse('true', mimetype="text/plain")

def club_comment_list(request, code, idx):
	post_info = Posts.objects.get(id=idx)
	board = Boards.objects.get(code=code)
	print code,idx;
	comment_list = Comments.objects.filter(post=post_info).order_by('-reg_date')
	return render_to_response(
		'club/common/comment.html',
		{
			'session' : request.session,
			'comment_list' : comment_list,
			'main_banner' : get_main_banner()
		}
	)
	
def club_comment_delete(request, code, idx):
	comment_info = Comments.objects.get(id=idx)	
	if comment_info.user.user_id == request.session['user_id']:
		comment_info.delete()
		return HttpResponse('success', mimetype="text/html")
	else:
		return HttpResponse('fail', mimetype="text/html")

def club_comment_edit(request, code, idx):
	comment_info = Comments.objects.get(id=idx)	
	if comment_info.user.user_id == request.session['user_id']:
		if request.method == 'POST':
			comment_info.comment = request.POST['content']
			comment_info.save()
			return HttpResponse('success', mimetype="text/html")
		else:	
			return render_to_response(
				'club/common/comment_edit.html',
				{
					'session' : request.session,
					'comment' : comment_info,
					'code'	  : code,
					'main_banner' : get_main_banner()
				}
			)
	else:
		return HttpResponse('false', mimetype="text/html")
	#return HttpResponse('fail', mimetype="text/html")

def image_upload(request, editor_id):
	if request.method == 'POST':
		
		upload_path = settings.STORAGE_PATH+'/'+request.POST['code']
		if not os.path.exists(upload_path):
			os.makedirs(upload_path)
		
		for field_name in request.FILES:
			uploaded_file = request.FILES[field_name]
		
		gen_name = GenPasswd()
		tmp_filename = (uploaded_file.name).split('.')
		file_ext = tmp_filename[1]
		gen_file_name = datetime.now().strftime('%Y_%m_%d') + '_' + (gen_name) + '.' + file_ext
		destination_path = upload_path+'/%s' % gen_file_name
		print destination_path
		destination = open(destination_path, 'wb+')
		for chunk in uploaded_file.chunks():
			destination.write(chunk)
		destination.close()

		return_html = '''<script type='text/javascript'>
			parent.parent.insertIMG("'''+editor_id+'''","'''+gen_file_name+'''");
			parent.parent.oEditors.getById["'''+editor_id+'''"].exec("SE_TOGGLE_IMAGEUPLOAD_LAYER");
			</script>'''
		return HttpResponse(return_html, mimetype="text/html")
		
	else:	
		return render_to_response(
			'club/image_upload.html',
			{
				'request' : request,			
				'user' : request.user,
				'session' : request.session,
				'editor_id' : editor_id,
				'main_banner' : get_main_banner()
			}
		)


def blog_push(request, id):
	post = Posts.objects.get(id=id)
	print post
		#인증메일 전송
	subject, from_email, to = post.title, 'jkimyhs@gmail.com', '9ousvp0movrhc@tumblr.com'

	msg = EmailMultiAlternatives(subject, post.content, from_email, [to])
	msg.attach_alternative(post.content, "text/html")
	msg.send()	
	return HttpResponse("success")

