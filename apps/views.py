# -*- coding: utf-8 -*-
from django.http import HttpResponse
from datetime import datetime
from libs.lib import *
from django.http import HttpResponseRedirect
from event.models import *
from movies.models import *
import urllib
from cStringIO import StringIO 
import Image
import time

def app_hotmovies(request):
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
		'apps/hotmovies.html',
		{
			'request' : request,
			'movies_info' : movies_info
		}
	)

def app_events(request, evt_type='all'):
	if evt_type == 'all':
		event_info = Events.objects.filter(status__in=['start']).order_by('-id')
	else:
		event_info = Events.objects.filter(type=evt_type, status__in=['start'])

	return render_to_response(
		'apps/events.html',
    	{
			'request' : request,
			'event_list' : event_info,
			'type' : evt_type
		}
    )

def image_proxy(request):
	url = base64.decodestring(request.GET['u'])
	contents = urllib.urlopen(url).read()
	return HttpResponse(contents, content_type='image/jpg')

def link_proxy(request):
	url = base64.decodestring(request.GET['u'])
	return HttpResponseRedirect(url)

def resize_remote_image(request):
	try:
		path, url, width, height = request.GET['path'], request.GET['url'], request.GET['width'],request.GET['height']
	except:
		return HttpResponse('파라미터를 정확하게 입력하세요.')
	img_data = urllib.urlopen(url) 
	img_io = StringIO(img_data.read()) 
	im = Image.open(img_io) 
	#print datetime.strftime('%Y-%m-%d')
	im.thumbnail((int(width), int(height)), Image.ANTIALIAS)
	urls = path+GenPasswd()+".jpg"
	im.save(urls)
	return HttpResponse(urls)
