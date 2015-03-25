# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from member.forms import *
from member.models import *
from movies.models import *
from event.models import *
from club.models import *
from libs.lib import *
from libs.api_request import *
from libs.digg_pagination import *
from django.http import HttpResponse
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Q
from django.views.decorators.cache import cache_page
import hashlib
import socket 
import datetime
import random
import time
import urllib 
from cStringIO import StringIO 
#import Image
from datetime import datetime

def err(request):
	return render_to_response(
		'500.html',
		{
			'request' : request,
			'user' : request.user, 
			'session' : request.session
		}
	)
	
def google_verify(request):
	return HttpResponse("google-site-verification: google6a507a904d8f981a.html")

def index(request):
	if 'pc' in request.GET:
		check = request.GET['pc']
	else:
		devices = ['iPad', 'iPod', 'iPhone', 'Android']
		for device in devices:
			result = (request.META['HTTP_USER_AGENT']).find(device)
			if result > -1:
				return HttpResponseRedirect('http://m.inthe-movie.com')


	imdb = imdbAPI()
	# 추천 핫 무비
	hot_movie = Movies.objects.filter(show = 'Y').order_by('?')
	# 이벤트 4개
	event_list = Events.objects.filter(status__in=['start','end']).order_by('-create_date')[:4]
	# 덕스클럽 웹진 2개
	reporter_board = Boards.objects.get(code='reporter')
	movie_board = Boards.objects.get(code='movie')
	performance_board = Boards.objects.get(code='performance')	
	review_list = Posts.objects.filter(board__in=[reporter_board]).order_by('-reg_date')[:2]
	# 일반 게시물 5개 
	club_list = Posts.objects.order_by('-reg_date')[:5]
	
	#배너 
	banner = ['<a href="https://inthe-movie.com/TheKillerElite/vlaah/"><img src="http://media.inthe-movie.com/killer/images/678x112.jpg" alt="main_banner"  style="border:2px solid #d9d9d9;" width="678" height="112" /></a>']
	
	random.shuffle(banner)
	
	return render_to_response(
		'index.html',
		{
			'request' : request,
			'user' : request.user, 
			'session' : request.session,
			'hot_movie' : hot_movie[0],
			'event_list' : event_list,
			'review_list' : review_list,
			'club_list' : club_list,
			'main_banner' : get_main_banner(),
			'search_keyword' : get_search_keyword()
			#'main_banner' : 'main_banner' : get_main_banner(),
		}
	)
		
def notice_loading(request):
	#공지사항
	notice = inthemovieNotice()
	notice_list = notice.getNotice()
	return render_to_response(
		'notice_load.html',
		{
			'request':request,
			'notice_list' : notice_list[:4]
		}
	)	
def main_tos(request):
	return render_to_response(
		'tos.html',
		{
			'request' : request,
			'user' : request.user, 
			'session' : request.session,
			'search_keyword' : get_search_keyword()
		}
	)
	
def main_private(request):
	return render_to_response(
		'private.html',
		{
			'request' : request,
			'user' : request.user, 
			'session' : request.session,
			'search_keyword' : get_search_keyword()
		}
	)		
		
def login(request):
	errors = []
	result = True
	form = LoginForm()
	if request.method == 'POST':
		return_url = request.POST['return_url']
		form = LoginForm(request.POST)
		
		password = hashlib.md5(request.POST['password']).hexdigest()
		if result == True:
			try:
				Users.objects.get(user_id=request.POST['user_id'])
			except ObjectDoesNotExist:
				errors.append({'type': 'user_id', 'msg': u'아이디가 올바르지 않습니다.'})
				result = False
		
		if result == True:
			try:
				Users.objects.get(user_id=request.POST['user_id'], password=password)
			except ObjectDoesNotExist:
				try:
					Users.objects.get(user_id=request.POST['user_id'], password=mysql_password(request.POST['password']))
					password = mysql_password(request.POST['password'])
				except ObjectDoesNotExist:
					errors.append({'type': 'password', 'msg':u'비밀번호가 올바르지 않습니다.'})
					result = False

		if result == True:
			try:
				Users.objects.get(user_id=request.POST['user_id'], password=password, is_auth='y')
			except ObjectDoesNotExist:
				result = False
				user = Users.objects.get(user_id=request.POST['user_id'])
				
				#인증코드 생성
				req_date = (user.reg_date).strftime('%Y-%m-%d %H:%M')
				auth_code = "inthe-movie.com" + user.user_id + 'asd$^# fqwer'+user.email + req_date + "inthe-movie.com"
				auth_code = hashlib.md5(auth_code).hexdigest()
				auth_url = 'https://inthe-movie.com/join/auth?user_id='+user.user_id+'&code='+auth_code

				#인증메일 전송
				contents = get_template('member/email/join_confirm.html')
				d = Context({ 'auth_url': auth_url })
				subject, from_email, to = '[인더무비] 회원가입인증 확인', 'contact@inthe-movie.com', user.email

				html_content = contents.render(d)
				msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
				msg.attach_alternative(html_content, "text/html")
				msg.send()				
				return render_to_response( 
					'common/common_message.html',
					{'message' : u'회원인증이 완료되지 않았습니다. email을 확인하여 인증 url에 접속해 주세요.'}
				)
		if result == True:
			user = Users.objects.get(user_id = request.POST['user_id'])
			if user.password == password:
				if user.is_admin == 'Y':
					request.session['is_admin']		= 'yes'
				else:
					request.session['is_admin']		= 'none'
				request.session['user_id']		= user.user_id
				request.session['nick_name']  = user.nick_name
				if return_url:
					return HttpResponseRedirect(return_url)
				else:
					return HttpResponseRedirect('/')
	else:
		form = LoginForm()
	
	return render_to_response(
		'member/login.html',
		{
		'request' : request,
		'session' : request.session,
		'form' : form,
		'errors' : errors,
		'search_keyword' : get_search_keyword()
		}
		)

def logout(request):
	request.session['user_id'] = ''
	request.session['nick_name'] = ''
	request.session['is_admin'] = ''
	return HttpResponseRedirect('/')

def member_find(request):
	if request.method == 'POST':
		user = None
		error = None
		try:
			gen_password = GenPasswd()
			user = Users.objects.get(name=request.POST['name'], email=request.POST['email'])
			user.password = hashlib.md5(gen_password).hexdigest()
			user.save()

			contents = get_template('member/email/find_form.html')
			d = Context({ 'user_id': user.user_id, 'password' : gen_password })
			subject, from_email, to = '[인더무비] 로그인정보 확인', 'contact@inthe-movie.com', user.email

			html_content = contents.render(d)
			msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
			msg.attach_alternative(html_content, "text/html")
			msg.send()
					
		except ObjectDoesNotExist:
			error = True	
		return render_to_response(
			'member/find_success.html',
			{
				'request' : request,
				'session' : request.session,
				'error'	  : error,
				'search_keyword' : get_search_keyword()
			}
		)
	else:
		return render_to_response(
			'member/find.html',
			{
				'request' : request,
				'session' : request.session,
				'search_keyword' : get_search_keyword()
			}
		)	

def join_validate(request):
	validate_type = request.POST['type']
	if validate_type == 'user_id':
		try:
			user_info = Users.objects.get(user_id = request.POST['values'])
			return HttpResponse(user_info.user_id, mimetype="text/html")
		except ObjectDoesNotExist:
			return HttpResponse('empty', mimetype="text/html")

	elif validate_type == 'nick_name':
		try:
			user_info = Users.objects.get(nick_name = request.POST['values'])
			return HttpResponse(user_info.nick_name, mimetype="text/html")
		except ObjectDoesNotExist:
			return HttpResponse('empty', mimetype="text/html")
		
	elif validate_type == 'email':
		try:
			user_info = Users.objects.get(email = request.POST['values'])
			return HttpResponse(user_info.email, mimetype="text/html")
		except ObjectDoesNotExist:
			return HttpResponse('empty', mimetype="text/html")
		

def join(request):
	errors = []
	result = True
	if request.method == 'POST':
			# 회원가입 
		user = Users.objects.create(
				user_id				 = request.POST['user_id'],
				password				= hashlib.md5(request.POST['password']).hexdigest(),
				name			= request.POST['name'],
				nick_name		   = request.POST['nick_name'],
				mobile_phone		= request.POST['mobile_phone'],
				email				   = request.POST['email'],
				ip			  = request.META['REMOTE_ADDR'],
				is_auth				 = 'n'
				)
			
		#포인트 로그 추가 
		point = Points.objects.create(
				user = user,
				type = 'get',
				point = 500,
				description = '회원가입 축하 포인트입니다.',
				ip = request.META['REMOTE_ADDR']
		)
			
		#가입축하 쪽지 추가
		'''message = Messages.objects.create(
				is_notice = 'y',
				sender_id = 'admin',
				recipient_id = request.POST['user_id'],
				content = '회원 가입을 축하드립니다.',
				ip = request.META['REMOTE_ADDR'],
				send_date = datetime.datetime.now()
		)'''

		#인증코드 생성
		req_date = (user.reg_date).strftime('%Y-%m-%d %H:%M')
		auth_code = "inthe-movie.com" + user.user_id + 'asd$^# fqwer'+user.email + req_date + "inthe-movie.com"
		auth_code = hashlib.md5(auth_code).hexdigest()
		auth_url = 'https://inthe-movie.com/join/auth?user_id='+user.user_id+'&code='+auth_code
		
		#인증메일 전송
		contents = get_template('member/email/join_confirm.html')
		d = Context({ 'auth_url': auth_url })
		subject, from_email, to = '[인더무비] 회원가입인증 확인', 'contact@inthe-movie.com', user.email

		html_content = contents.render(d)
		msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
		msg.attach_alternative(html_content, "text/html")
		msg.send()		
		
		request.session['confirm_email'] = request.POST['email']
		return HttpResponseRedirect('/join/success/')
	else:
		form = JoinForm()

	return render_to_response(
		'member/join.html',
		{
			'request' : request,
			'session' : request.session,
			'form' : form,
			'search_keyword' : get_search_keyword()
		}
	)

def join_success(request):
	return render_to_response(
		'member/join_success.html',
		{
			'request' : request,
			'session' : request.session,
			'search_keyword' : get_search_keyword()
		}
	)	
	
def join_auth(request):

	user = Users.objects.get(user_id = request.GET['user_id'])
	
	if user.is_auth == 'y':
		return render_to_response( 
			'common/common_message.html',
			{'message' : u'exist'.encode('utf-8') }
		)

	req_date = (user.reg_date).strftime('%Y-%m-%d %H:%M')
	auth_code = "inthe-movie.com" + user.user_id + 'asd$^# fqwer'+user.email + req_date + "inthe-movie.com"
	auth_code = hashlib.md5(auth_code).hexdigest()
	
	if request.GET['code'] == auth_code:
		user.is_auth = 'y'
		user.save()
		return render_to_response( 
			'common/common_message.html',
			{'message' : u'sucess'.encode('utf-8')}
		)
	else:
		return render_to_response( 
			'common/common_message.html',
			{'message' : u'fail'.encode('utf-8')}
		)

def mypage(request, user_id):
		user = Users.objects.get(user_id = user_id)
		variables = RequestContext(request, {
				'user' : user,
				'session' : request.session
		})
		return render_to_response(
				'member/mypage.html',
			{'request' : request,
			 'user' : request.user,
			 'session' : request.session,
			 'main_banner' : get_main_banner(),
			 'search_keyword' : get_search_keyword()
			 }
		)

def mypage_point(request, user_id):
	page = 1
	if 'page' in request.GET:
		page = request.GET['page']
	#회원정보 
	user_info = Users.objects.get(user_id = user_id)
		
	#타입별 포인트 내역 가져오기 
	type = request.GET.has_key('type')
		
	if 'type' in request.GET:
		if request.GET['type']:
			point_list = user_info.points_set.filter(type=request.GET['type']).order_by('-id')
		else:
			point_list = user_info.points_set.order_by('-id')
		type= request.GET['type']
	else:
		point_list = user_info.points_set.order_by('-id')
		type= 'all'
	paginator = Paginator(point_list, 10)

	try:
		point_list = paginator.page(page)
	except (EmptyPage, InvalidPage):
		point_list = paginator.page(paginator.num_pages)

	digg = digg_pagination(paginator.page(page))


	return render_to_response(
		'member/mypage_point.html',
		{
			'request' : request,
			'user_info' : user_info,
			'session' : request.session,
			'point_list' : point_list,
			'page'  : page,
			'digg' : digg,
			'type' : type,
			'main_banner' : get_main_banner(),
			'search_keyword' : get_search_keyword()
		}
	)
		
def mypage_message(request, user_id):
	page = 1
	if 'page' in request.GET:
		page = request.GET['page']
	type_flag = request.GET.has_key('type')
	if 'type' in request.GET:
		if request.GET['type'] == 'send':
			message_list = Messages.objects.filter(recipient_id=user_id).order_by('-id')
		elif request.GET['type'] == 'recive':
			message_list = Messages.objects.filter(sender_id=user_id).order_by('-id')
		else:
			message_list = Messages.objects.filter(Q(sender_id=user_id) | Q(recipient_id=user_id)).order_by('-id')
		type = request.GET['type']
	else:
		message_list = Messages.objects.filter(Q(sender_id=user_id) | Q(recipient_id=user_id)).order_by('-id')
		type='all'
	paginator = Paginator(message_list, 10)

	try:
		message_list = paginator.page(page)
	except (EmptyPage, InvalidPage):
		message_list = paginator.page(paginator.num_pages)

	digg = digg_pagination(paginator.page(page))
			
	return render_to_response(
		'member/mypage_message.html',
		{
			'request' : request,
			'user_info' : request.user,
			'session' : request.session,
			'message_list' :message_list,
			'page'  : page,
			'digg' : digg,
			'type' : type,
			'main_banner' : get_main_banner(),
			'search_keyword' : get_search_keyword()
		}
	)
		
def mypage_message_post(request, user_id):
		errors = []
		if request.method == 'POST':
			#form = MessageForm(request.POST)
			#가입축하 쪽지 추가
			try:
				Users.objects.get(user_id=request.POST['recived_id'])
			except ObjectDoesNotExist:
				errors.append('받는사람의 아이디가 가입되어 있지 않습니다.')
			
			if errors:
				return render_to_response(
					'member/mypage_message_post.html',
					{
						'user' : request.user,
						'session' : request.session,
						'errors' : errors,
						'search_keyword' : get_search_keyword()
					}
				)
			
			message = Messages.objects.create(
					is_notice = 'n',
					sender_id = user_id,
					recipient_id = request.POST['recived_id'],
					content = request.POST['content'],
					ip = request.META['REMOTE_ADDR']
			)
			return HttpResponseRedirect('/user/'+user_id+'/message/?type=send')
		else:
			form = MessageForm()
				 
		return render_to_response(
			'member/mypage_message_post.html',
			{
				'request' : request,
				'user_info' : request.user,
				'session' : request.session,
				'search_keyword' : get_search_keyword()
			}
		)

def mypage_message_read(request, user_id, idx):
		message_article = Messages.objects.get(id=idx)
		
		if not message_article.read_date:
				message_article.read_date = datetime.datetime.now()
				message_article.save()

		return render_to_response(
			'member/mypage_message_read.html',
			{
				'request' : request,
		 		'user_info' : request.user,
				'session' : request.session,
				'message_article' : message_article,
				'search_keyword' : get_search_keyword()
			}
		)

def mypage_message_delete(request, user_id, idx):
	message_article = Messages.objects.get(id=idx)
	message_article.delete()
	return HttpResponseRedirect('/user/'+user_id+'/message')

def mypage_info(request, user_id):
		errors = []
		result = []
		user_info = Users.objects.get(user_id = user_id)
		if request.method == 'POST':
			#form = JoinForm(request.POST)
			try:
				Users.objects.get(
					user_id=user_id, 
					password=hashlib.md5(request.POST['password_now']).hexdigest()
				)
			except ObjectDoesNotExist:
				try:
					Users.objects.get(
						user_id=user_id, 
						password=mysql_password(request.POST['password_now'])
					)
				except ObjectDoesNotExist:
					errors.append(u"기존 비밀번호를 확인해주세요.")
					return render_to_response(
						'member/mypage_info.html',
						{
							'request' : request,
							'user' : request.user,
							'session' : request.session,
							'user_info' : user_info,
							'errors' : errors,
							'main_banner' : get_main_banner(),
							'search_keyword' : get_search_keyword()
						}
					)
					
			#패스워드를 변경했다면!
			if request.POST['password']:
				user_info.password = hashlib.md5(request.POST['password']).hexdigest()

			user_info.name = request.POST['name']
			user_info.nick_name = request.POST['nick_name']
			user_info.mobile_phone = request.POST['mobile_phone']
			user_info.email = request.POST['email']
			user_info.save()
			
			result.append(u"회원정보가 성공적으로 수정되었습니다.")

		return render_to_response(
			'member/mypage_info.html',
			{
				'request' : request,
				'user' : request.user,
				'session' : request.session,
				'user_info' : user_info,
				'result' : result,
				'main_banner' : get_main_banner(),
				'search_keyword' : get_search_keyword()
			}
		)

def member_dropout(request, user_id):
	user_info = Users.objects.get(user_id = user_id)
	if request.method == 'POST':
		if request.session['user_id'] == user_info.user_id:
			dropout = Dropouts.objects.create(
				user_id = user_info.user_id,
				name = user_info.name
			)
			user_info.delete()
			request.session['user_id']	= ''
			request.session['nick_name'] = ''
			return HttpResponseRedirect('/?dropout=success')
			
	return render_to_response(
		'member/mypage_dropout.html',
		{
			'request' : request,
			'user' : request.user,
			'session' : request.session,
			'user_info' : user_info,
			'main_banner' : get_main_banner(),
			'search_keyword' : get_search_keyword()
		}
	)

def movie_search(request):
	if 'q' in request.GET:
		movie_list = Movies.objects.filter(title_kor__contains = request.GET['q']).order_by('-id')[:50]
		cnt = len(movie_list)
		if movie_list != None:
			if cnt == 1:
				return HttpResponseRedirect('/'+str(movie_list[0].title_url))

		return render_to_response(
			'movie_search.html',
			{
				'request' : request,
				'user' : request.user,
				'session' : request.session,
				'movies_info' : movie_list,
				'main_banner' : get_main_banner(),
				'search_keyword' : get_search_keyword()
			}
		)
	else:
		return HttpResponseRedirect('/')



def get_banner(request):
	return render_to_response(
		'banner.html',
		{
			'request' : request,
			'main_banner' : get_main_banner()
		}
	)	
