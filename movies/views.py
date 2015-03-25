# -*- coding: utf-8 -*-
from django.http import HttpResponse
from datetime import datetime
from libs.lib import *
from libs.digg_pagination import *
from django.http import HttpResponseRedirect
from movies.models import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage
import simplejson
import urllib
from libs.api_request import *
from event.models import *
from operator import itemgetter
def movies_main(request):
	hot_movie = Movies.objects.filter(show = 'Y').order_by('?')
	hotmovies = hot_movie[0]
	hot_movie_vod = hotmovies.collectdata_set.filter(type__contains='vod', swf_url__isnull=False)[:1]
	vod_content = None
	for vod in hot_movie_vod:
		vod_content = vod
	movies_info = []
	if 'premovie' in request.GET:
		movies_info = Movies.objects.filter(type='naver_premovie',is_collected='T')
	elif 'current' in request.GET:
		movies_info = Movies.objects.filter(type='naver_current',is_collected='T')
	elif 'top10' in request.GET:
		movies_info = Movies.objects.filter(is_collected='T', is_keyword='T')
	else:
		movies_info = Movies.objects.filter(is_collected='T', is_keyword='T')
	return render_to_response(
		'movies/main.html',
		{
		'request' : request,
		'user' : request.user,
		'session' : request.session,
		'movies_info' : movies_info,
		'hot_movie' : hotmovies,
		'hot_movie_vod' : vod_content,
		'main_banner' : get_main_banner(),
		'search_keyword' : get_search_keyword()
		}
	)

def hotmovie_main(request, movie_title):
	movie_title = urllib.unquote(movie_title).decode('utf-8')
	url_title = movie_title
	movie_info	= Movies.objects.filter(title_url = movie_title)
	movie_info = movie_info[0]
	
	try:
		photo_info	= movie_info.collectdata_set.filter(type__contains='image')[:4]
	except:
		photo_info = None

	vod_info	= movie_info.collectdata_set.filter(type__contains='vod')[1:5]
	blog_info	= movie_info.collectdata_set.filter(type__in=['daum_view', 'naver_blog']).order_by('-id')[:4]
	news_info 	= movie_info.collectdata_set.filter(type__contains='naver_news').order_by('-id')[:4]
	movie_info_vod = movie_info.collectdata_set.filter(type='vod')[:1]
	vod_content = None
	for vod in movie_info_vod:
		vod_content = vod

	title = movie_info.title_kor
	title_split = title.split(':')
	title = title_split[0]
	dash_split = title.split('-')
	title = dash_split[0]
	
	return render_to_response(
		'movies/hotmovie_main.html',
		{
			'request' : request,
			'url_title': url_title,
			'user' : request.user,
			'session' : request.session,
			'title' : movie_title,
			'photo_list' : photo_info,
			'vod_list' : vod_info,
			'movie_info' : movie_info,
			'blog_list' : blog_info,
			'movie_info_vod' : vod_content,
			'news_info' : news_info,
			'main_banner' : get_main_banner(),
			'search_keyword' : get_search_keyword()
		}
	)


def hotmovie_sns(request, movie_title, type):
	
	movie_info	= Movies.objects.filter(title_url = movie_title)
	movie_info = movie_info[0]	
	title = movie_info.title_kor
	title_split = title.split(':')
	title = title_split[0]
	dash_split = title.split('-')
	title = dash_split[0]
	if type=='mixsns' : 
		
		sns_items = [] # SNS아이템을 싹 몽라두는곳
		
		# Twitter Data Initalize
		data_url = 'http://search.twitter.com/search.json'
		form = {"q": title.encode('utf-8'), "rpp": 4 }
		form = urllib.urlencode(form)
		sns_list_twitter = simplejson.load(urllib.urlopen(data_url+'?'+form)).get('results')
		
		for list in sns_list_twitter:
			sns_items.append({
								"user_url"		: 'http://twitter.com/'+ list.get('from_user'),
								"thumbnail_url"	: list.get('profile_image_url'),
								"user_name"		: list.get('from_user'),
								"contents"		: list.get('text'),
								"type"			: "twitter",
								"created_at"	: (datetime.datetime.strptime(list.get('created_at'), '%a, %d %b %Y %H:%M:%S +0000') + datetime.timedelta(hours=9))
							});
		

		#Me2Day Data Initalize
		me2day_url = 'http://me2day.net/search.json'
		form = {"query": "(" + title.encode('utf-8') + ")", "search_at": "all", "count": 4 }
		form = urllib.urlencode(form)
		sns_list_me2day = simplejson.load(urllib.urlopen(me2day_url + "?" + form))	
		
		for list in sns_list_me2day:
			sns_items.append({
								"user_url"		: 'http://me2day.net/'+ list.get('author').get('id'),
								"thumbnail_url"	: list.get('author').get('face'),
								"user_name"		: list.get('author').get('nickname'),
								"contents"		: list.get('body'),
								"type"			: "me2day",
								"created_at"	: datetime.datetime.strptime(list.get('pubDate'), '%Y-%m-%dT%H:%M:%S+0900')
							});
							
		#data Sorting
		sns_items.sort(key=lambda x: x["created_at"], reverse=True)
		if request.GET['date'] != "":		
			templist = sns_items[:]	
			for item in templist:
				if datetime.datetime.strptime(request.GET['date'],"%Y-%m-%d %H:%M:%S") >= item['created_at']:
					sns_items.remove(item)

		return render_to_response(
			'movies/hotmovie_right_sns.html',
			{
				'request':request,
				'sns_list':sns_items
			}
		)

	elif type=='twitter' :
		twitter_url = 'http://search.twitter.com/search.json'
		form = {"q": title.encode('utf-8') }
		form = urllib.urlencode(form)
		result = simplejson.load(urllib.urlopen(twitter_url+'?'+form))	
		sns_list = result.get('results')
	elif type=="me2day":
		me2day_url = 'http://me2day.net/search.json?query=('+ title.encode('utf-8')+')&search_at=all'
		result = simplejson.load(urllib.urlopen(me2day_url))	
		sns_list = result

	return render_to_response(
		'movies/hotmovie_twitter.html',
		{
			'request':request,
			'type':type,
			'sns_list':sns_list,
			'movie_info' : movie_info
		}
	)

	
	
	
def hotmovie_blog(request, movie_title, page=1):
	movie_info	= Movies.objects.filter(title_url = movie_title)
	movie_info = movie_info[0]
	blog_info	= movie_info.collectdata_set.filter(type__in=['daum_view', 'naver_blog']).order_by('-id')	
	blog_count = len(blog_info)

	movie_info_vod = movie_info.collectdata_set.filter(type__contains='vod', swf_url__isnull=False)[:1]
	vod_content = None
	for vod in movie_info_vod:
		vod_content = vod

	paginator = Paginator(blog_info, 10)

	try:
		blog_info = paginator.page(page)
	except (EmptyPage, InvalidPage):
		blog_info = paginator.page(paginator.num_pages)
		
	digg = digg_pagination(paginator.page(page))
	return render_to_response(
		'movies/hotmovie_blog.html',
		{
			'request' : request,
			'user' : request.user,
			'session' : request.session,
			'title' : movie_title,
			'movie_info' : movie_info,
			'posts' : blog_info,
			'page' : page,
			'blog_count' : blog_count,
			'hotmovie_menu' :'blog',
			'digg' : digg,
			'movie_info_vod' : vod_content,
			'main_banner' : get_main_banner(),
			'search_keyword' : get_search_keyword()
		}
	)
	
def hotmovie_video(request, movie_title, page=1):
	movie_info	= Movies.objects.filter(title_url = movie_title)
	movie_info = movie_info[0]
	vod_info	= movie_info.collectdata_set.filter(type__contains='vod')
	vod_count = len(vod_info)
	
	movie_info_vod = movie_info.collectdata_set.filter(type__contains='vod', swf_url__isnull=False)[:1]
	vod_content = None
	for vod in movie_info_vod:
		vod_content = vod	
	
	paginator = Paginator(vod_info, 16)

	try:
		vod_info = paginator.page(page)
	except (EmptyPage, InvalidPage):
		vod_info = paginator.page(paginator.num_pages)
	
	digg = digg_pagination(paginator.page(page))
	return render_to_response(
		'movies/hotmovie_video.html',
		{
			'request' : request,
			'user' : request.user,
			'session' : request.session,
			'title' : movie_title,
			'posts' : vod_info,
			'movie_info' : movie_info,
			'page' : page,
			'vod_count' : vod_count,
			'hotmovie_menu' :'video',
			'digg' : digg,
			'movie_info_vod' : vod_content,
			'main_banner' : get_main_banner(),
			'search_keyword' : get_search_keyword()
		}
	)
		
def hotmovie_photo(request, movie_title, page=1):
	movie_info	= Movies.objects.filter(title_url = movie_title)
	movie_info = movie_info[0]
	photo_info	= movie_info.collectdata_set.filter(type__contains='image')
	photo_count = len(photo_info)
	
	movie_info_vod = movie_info.collectdata_set.filter(type__contains='vod', swf_url__isnull=False)[:1]
	vod_content = None
	for vod in movie_info_vod:
		vod_content = vod	
	paginator = Paginator(photo_info, 16)
	
	try:
		photo_info = paginator.page(page)
	except (EmptyPage, InvalidPage):
		photo_info = paginator.page(paginator.num_pages)

	digg = digg_pagination(paginator.page(page))
	return render_to_response(
		'movies/hotmovie_photo.html',
		{
			'request' : request,
			'user' : request.user,
			'session' : request.session,
			'title' : movie_title,
			'movie_info' : movie_info,
			'posts' : photo_info,
			'page' : page,
			'photo_count' : photo_count,
			'hotmovie_menu' :'photo',
			'digg' : digg,
			'movie_info_vod' : vod_content,
			'main_banner' : get_main_banner(),
			'search_keyword' : get_search_keyword()
		}
	)

def hotmovie_vlaah(request, movie_title):
	#print request.META['HTTP_HOST']
	# 인더무비 SNS
	'''
	try:
		session_id =  request.session['user_id']
		try:
			ids = Users.objects.get(user_id = session_id)
			sns_info = 	Sns.objects.get(user = ids)
			print sns_info.user.user_id
		except:
			print "not in Database"
	except:
		print "not login"
	'''

	movie_info	= Movies.objects.filter(title_url = movie_title)
	movie_info = movie_info[0]
	movie_info_vod = movie_info.collectdata_set.filter(type__contains='vod', swf_url__isnull=False)[:1]
	vod_content = None
	for vod in movie_info_vod:
		vod_content = vod	
	title = movie_info.title_kor
	title_split = title.split(':')
	title = title_split[0]
	dash_split = title.split('-')
	title = dash_split[0]
	
	#트위터 API
	twitter_url = 'http://search.twitter.com/search.json'
	form = {"q": title.encode('utf-8') }
	form = urllib.urlencode(form)
	result = simplejson.load(urllib.urlopen(twitter_url+'?'+form))	
	twitter_list = result.get('results')
	
	#print request.COOKIES
	if request.is_ajax():
		comment_id = request.GET['id']
		comment_list = movie_info.socialcomment_set.filter(id__lt = comment_id).order_by('-id')[:20]
		return render_to_response(
			'movies/hotmovie_vlaah_list.html',
			{
				'request' : request,
				'comment_list' : comment_list,
				'comment_number' : comment_list.count(), 
				'movie_info' : movie_info,
				'movie_info_vod' : vod_content,
				'main_banner' : get_main_banner(),
				'twitter_list' : twitter_list
			}
		)
	else:
		comment_list = movie_info.socialcomment_set.filter().order_by('-id')[:20]
		#print comment_list.count()
	event_info = None
	try:
		event_info = Events.objects.get(movie=movie_info)
	except:
		pass
	
	facebook_profile = twitter_profile = me2day_profile = None
	
	try:
		user_info = Users.objects.get(user_id = request.session['user_id'])
		try:
			facebook_profile = Sns.objects.get(user=user_info,service='facebook')
		except:
			try:
				if request.COOKIES.has_key('oauth_facebook'):
					sns_info = Sns.objects.create(
							user = user_info,
							service = 'facebook',
							oauth_token = request.COOKIES['oauth_facebook']
						)
					facebook_profile = simplejson.load(urllib.urlopen(
							"https://graph.facebook.com/me?" +
							urllib.urlencode(dict(access_token=request.COOKIES['oauth_facebook']))))
			except:
				pass
		try:
			me2day_profile = Sns.objects.get(user=user_info,service='me2day')
		except:
			try:
				if request.COOKIES.has_key('oauth_me2day'):
					sns_info = Sns.objects.create(
							user = user_info,
							service = 'me2day',
							oauth_token = request.COOKIES['oauth_me2day']
						)
					me2day_profile = request.COOKIES['oauth_me2day']
			except:
				pass

		try:
			twitter_profile = Sns.objects.get(user=user_info,service='twitter')
		except:
			try:
				if request.COOKIES.has_key('oauth_twitter'):
					sns_info = Sns.objects.create(
						user = user_info,
						service = 'twitter',
						oauth_token = request.COOKIES['oauth_twitter']
					)
					twitter_profile = request.COOKIES['oauth_twitter']
			except:
				pass
	except:
		if request.COOKIES.has_key('oauth_facebook'):
			facebook_profile = simplejson.load(urllib.urlopen(
		                "https://graph.facebook.com/me?" +
		                urllib.urlencode(dict(access_token=request.COOKIES['oauth_facebook']))))
		if request.COOKIES.has_key('oauth_me2day'):
			me2day_profile = request.COOKIES['oauth_me2day']
		if request.COOKIES.has_key('oauth_twitter'):
			twitter_profile = request.COOKIES['oauth_twitter']

	#'twitter_list' : twitter_list
	
	return render_to_response(
		'movies/hotmovie_vlaah.html',
		{
			'request' : request,
			'user' : request.user,
			'session' : request.session,
			'title' : movie_title,
			'movie_info' : movie_info,
			'facebook_profile' : facebook_profile,
			'me2day_profile' : me2day_profile,
			'twitter_profile' : twitter_profile,
			'comment_list' : comment_list,
			'event_info' : event_info,
			'main_banner' : get_main_banner(),
			'twitter_list' : twitter_list,
			'comment_number' : comment_list.count(),
			'comment_count' : len(twitter_list) + comment_list.count(),
			'movie_info' : movie_info,
			'movie_info_vod' : vod_content,
			'search_keyword' : get_search_keyword()
		}
	)

def hotmovie_review(request, movie_title):
	return render_to_response(
		'movies/hotmovie_review.html',
		{
			'request' : request,
			'user' : request.user,
			'session' : request.session,
			'title' : movie_title,
			'main_banner' : get_main_banner(),
			'search_keyword' : get_search_keyword()
		}
	)
	
def hotmovie_news(request, movie_title, page=1):
	movie_info	= Movies.objects.filter(title_url = movie_title)
	movie_info = movie_info[0]
	news_info	= movie_info.collectdata_set.filter(type='naver_news').order_by('-id')	
	news_count = len(news_info)

	movie_info_vod = movie_info.collectdata_set.filter(type__contains='vod', swf_url__isnull=False)[:1]
	vod_content = None
	for vod in movie_info_vod:
		vod_content = vod

	paginator = Paginator(news_info, 10)

	try:
		news_info = paginator.page(page)
	except (EmptyPage, InvalidPage):
		news_info = paginator.page(paginator.num_pages)

	digg = digg_pagination(paginator.page(page))
	return render_to_response(
		'movies/hotmoive_news.html',
		{
			'request' : request,
			'user' : request.user,
			'session' : request.session,
			'title' : movie_title,
			'movie_info' : movie_info,
			'posts' : news_info,
			'page' : page,
			'blog_count' : news_count,
			'hotmovie_menu' :'news',
			'digg' : digg,
			'movie_info_vod' : vod_content,
			'main_banner' : get_main_banner(),
			'search_keyword' : get_search_keyword()
		}
	)	