# -*- coding: utf-8 -*-
from jinja2 import FileSystemLoader, Environment

from django.http import HttpResponse
from django.conf import settings
from django.template import RequestContext

import urlparse
import urllib
import re
import hashlib
import os
import random
from event.models import *
from admin.models import *
from movies.models import *
import datetime
import base64

def get_search_keyword():
	movie_info = Movies.objects.all().order_by('?')[:1]
	return movie_info[0].title_kor

def mysql_password(str):
	pass1 = hashlib.sha1(str).digest()
	pass2 = hashlib.sha1(pass1).hexdigest()
	return "*" + pass2.upper()


def GenPasswd():
	import subprocess
	import random

	password = ''.join([random.choice('ABCDEFGHIJKLMNOPQRSTUV\
	WXYZabcdefghijklmnopqrstuvwxyz1234567890') for i in range(10)])
	return password

template_dirs = getattr(settings,'TEMPLATE_DIRS')
default_mimetype = getattr(settings, 'DEFAULT_CONTENT_TYPE')
env = Environment(loader=FileSystemLoader(template_dirs))

def render_to_response(filename, context={},mimetype=default_mimetype):
    template = env.get_template(filename)
    rendered = template.render(**context)
    return HttpResponse(rendered,mimetype=mimetype)

def datetimeformat(value, format='%H:%M / %Y-%m-%d'):
	return value.strftime(format)

def createRate(count, star_type, type):
	returns =''
	if type:
		for i in range(5):
			if count>0:
				returns = returns+'<img src=\'/images/icon_total_star_on.png\' alt=\'star\'/>\n'
			else:
				returns = returns+'<img src=\'/images/icon_total_star_off.png\' alt=\'star\'/>\n'
			count = count - 1
	else:	
		for i in range(5):
			if count>0:
				returns = returns+'<img src=\'/images/icon_star_on.png\' alt=\'star\'/>\n'
			else:
				returns = returns+'<img src=\'/images/icon_star_off.png\' alt=\'star\'/>\n'
			count = count - 1
	return returns

def rate_percent(value):
	value = value * 10
	return str(value)+'%' 

def get_round(value):
	return round(value,1)
	
def getrating(value, star_type,type=None):
	rating_result = ''
	if value>9.9:
		rating_result = createRate(5, star_type,type)
	elif value>7.9:
		rating_result = createRate(4, star_type,type)
	elif value>5.9:
		rating_result = createRate(3, star_type,type)
	elif value>3.9:
		rating_result = createRate(2, star_type,type)
	elif value>2.0:
		rating_result = createRate(1, star_type,type)
	else:
		rating_result = createRate(0, star_type,type)
	return rating_result	
	
def urlencode(uri, **query):
	parts = list(urlparse.urlparse(uri))
	q = urlparse.parse_qs(parts[4])
	q.update(query)
	parts[4] = urllib.urlencode(q)
	return urlparse.urlunparse(parts)

def create_id_link(value):
	return re.sub(r'[@]+([A-Za-z0-9-_]+)',r'@<a href="http://twitter.com/\1" class="social_link" target="_blank">\1</a>', value)

def create_link(value):
	pattern = re.compile(r"(^|[\n ])(([\w]+?://[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)", re.IGNORECASE | re.DOTALL)
	return pattern.sub(r'\1<a href="\2" class="social_link" target="_blank">\2</a>', value)

def strrepl(value ,cnt):
	return value[:cnt]
	
def nl2br(value):
	return value.replace('\n','<br />\n')

def getTarget(value):
	value = value.replace('http://www.ducksmovie.net/gnuboard/data/','https://inthe-movie.com/files/')
	pattern = re.compile(r"(\<img )([^\>]*)(\>)", re.IGNORECASE | re.DOTALL)
	#return pattern.sub(r'\1 name="target_resize_image[] " \2 \3', value)
	return pattern.sub(r'\1  onload="javascript:fitImageSize(this);"  name="target_resize_image[]" \2 \3', value)
	
def st_replace(value,froms,to):
	return value.replace(froms,to)

def get_event_type(value):
	if value=='preview':
		return u'시사회'
	elif value=='show':
		return u'공연'
	elif value=='reserve':
		return u'예매권'
	else:
		return u'기타'
	
def strip_tags(value):
	value = value.replace("&lt;","<")
	value = value.replace("&gt;",">")
	return re.sub(r'<[^>]*?>', '', value)
	
def get_thumbnail_url(value, size, path):
	url = ''
	if path == 'web':
		url = value
	else:
		url = 'https://inthe-movie.com'+path + value
	
	try:
		im = get_thumbnail(url, size, crop='center', quality=99)
	except Exception as e:
		return '/images/no15898.png'
	
	return '/'+im.url
		
def url_encode(value):
	return urllib.unquote(value)
	
def rating_roundup(value):
	return round(value, 1)

def get_lnb(value, obj=None):
	if len(value.split(".")) < 2:
		return ""
	template = env.get_template(value.split(".")[0] + "/_local.html")
	rendered = template.render(c = value.split(".")[1], obj = obj)
	return rendered

def get_lnb_for_path(value, movie_info):
	
	if len(value.split("/")) < 3:
		tmp = ""
	else:
		tmp = value.split("/")[2]
	
	template = env.get_template("movies/_local_hotmovie.html")
	rendered = template.render(c = tmp, movie_info = movie_info)
	return rendered

def get_belongtime(value):
	
	belong = datetime.datetime.now() - value
	
	if belong.days > 0:
		return belong.strfstr("%Y-%m-%d")
	elif belong.hours > 0:
		return belong.hours + "시간 전"
	elif belong.minutes > 0:
		return belong.minutes + "분 전"
	elif belong.seconds > 0:
		return "방금 전"
	
	return "3분전"

def get_video_attr(value):

    _href = ""
    _class = ""

    if (value.swf_url):
    	_href = "/link_proxy/?u=" + base64.encodestring(value.swf_url)
        _class = "single_vod_swf"
    else:
    	_href = "/link_proxy/?u=" + base64.encodestring(value.link_url)
        _class = "single_vod"

    return "class=\"" + _class + "\" href=\"" + _href + "\""



def base64encode(s):
	if not (s==None):
		return base64.encodestring(s)
	else:
		return s


def split_facebook(s, index):
	fb = s.split('/')
	return fb[index]

def event_request_number(index):
	view_info = Events.objects.get(id=index)

	notin_list = []
	for panalty in Panalty.objects.all():
		notin_list.append(panalty.user.id)

	print notin_list
	request_list = None
	request_list = view_info.request_set.order_by('-ip_addr','-req_date')
	req_list = []

	def check_notin(notin_list, reqs):
		for notin in notin_list:
			try:
				if reqs.user.id == notin:
					return 'true'
			except:
				return 'false'
		return 'false'

	for req in request_list:
		result = check_notin(notin_list, req)
		if result == 'false':
			req_list.append(req)

	req_count = len(req_list)
	return req_count

env.filters['split_facebook'] = split_facebook
env.filters['base64encode'] = base64encode
env.filters['url_encode'] = url_encode
env.filters['urlencode'] = urlencode
env.filters['datetimeformat'] = datetimeformat
env.filters['getrating'] = getrating
env.filters['create_id_link'] = create_id_link
env.filters['create_link'] = create_link
env.filters['strrepl'] = strrepl
env.filters['nl2br'] = nl2br
env.filters['getTarget'] = getTarget
env.filters['st_replace'] = st_replace
env.filters['strip_tags'] = strip_tags
env.filters['get_thumbnail_url'] = get_thumbnail_url
env.filters['rating_roundup'] = rating_roundup
env.filters['rate_percent'] = rate_percent
env.filters['get_lnb'] = get_lnb
env.filters['get_lnb_for_path'] = get_lnb_for_path
env.filters['get_video_attr'] = get_video_attr
env.filters['get_belongtime'] = get_belongtime
env.filters['event_type'] = get_event_type
env.filters['get_round'] = get_round
env.filters['event_request_number'] = event_request_number
class BannerData:
    main = None
    right_top = None
    right_down = None

def get_main_banner():
	bannerData = BannerData()
	main_banner=[] #메인 상단배너
	right_banner_top=[] # 오른쪽 상단배너
	right_banner_down=[]  # 오른쪽 하단배너
	root_url = "https://inthe-movie.com"
	today = datetime.date.today()
	main_bannerlist = Banner.objects.filter(position__in=['main_top'] ,start_date__lte=datetime.date.today(),last_date__gte=datetime.date.today()).order_by('?')
	right_top_bannerlist = Banner.objects.filter(position__in=['right_1'],start_date__lte=datetime.date.today(),last_date__gte=datetime.date.today()).order_by('?')
	right_down_bannerlist = Banner.objects.filter(position__in=['right_2'],start_date__lte=datetime.date.today(),last_date__gte=datetime.date.today()).order_by('?')

	if not main_bannerlist:
		bannerData.main =""
	else:
		tag= "<a href=\"/link_proxy/?u=%s\" target=\"%s\"><img src=\"%s/files/banner_files/%s\" alt=\"main_banner\"  style=\"border:2px solid #d9d9d9;\" width=\"678\" height=\"112\" /></a>" % (base64.encodestring(main_bannerlist[0].link), main_bannerlist[0].blank, root_url, main_bannerlist[0].banner_root)
		bannerData.main = tag

	if not right_top_bannerlist:
		bannerData.right_top =""
	else:
		tag= "<a href=\"/link_proxy/?u=%s\" target=\"%s\"><img src=\"%s/files/banner_files/%s\" alt=\"main_banner\"  style=\"border:2px solid #d9d9d9;\" width=\"278\"   /></a>" % (base64.encodestring(right_top_bannerlist[0].link), right_top_bannerlist[0].blank,root_url, right_top_bannerlist[0].banner_root)
		bannerData.right_top = tag

	if not right_down_bannerlist:
		bannerData.right_down =""
	else:
		tag= "<a href=\"/link_proxy/?u=%s\" target=\"%s\"><img src=\"%s/files/banner_files/%s\" alt=\"main_banner\"  style=\"border:2px solid #d9d9d9;\" width=\"278\"   /></a>" % (base64.encodestring(right_down_bannerlist[0].link), right_down_bannerlist[0].blank,root_url, right_down_bannerlist[0].banner_root)
		bannerData.right_down = tag

	return bannerData
