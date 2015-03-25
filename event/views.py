# -*- coding: utf-8 -*-
from django.http import HttpResponse
import datetime
from libs.lib import *
from django.http import HttpResponseRedirect
from event.models import *
from member.models import *
import simplejson

def events_main(request, evt_type='all'):
	if evt_type == 'all':
		event_info = Events.objects.filter(status__in=['start']).order_by('-id')
	else:
		event_info = Events.objects.filter(type=evt_type, status__in=['start'])

	return render_to_response(
		'events/main.html',
    	{
			'request' : request,
			'user' : request.user,
			'session' : request.session,
			'event_list' : event_info,
			'type' : evt_type,
			'main_banner' : get_main_banner(),
			'search_keyword' : get_search_keyword()
		}
    )

def events_view(request, idx):
	event_info = Events.objects.get(id=idx)	
	request_info = None
	user_info = None
	try:
		if 'user_id' in request.session:
			if request.session['user_id']:
				user_info = Users.objects.get(user_id=request.session['user_id'])
				request_info = Request.objects.get(event=event_info, user=user_info)
		else:
			pass
	except Exception as e:
		pass
	
	return render_to_response(
		'events/event_view.html',
		{
			'request' : request,
			'user' : request.user,
			'session' : request.session,
			'view' : event_info,
			'request_info' : request_info,
			'main_banner' : get_main_banner(),
			'search_keyword' : get_search_keyword()
		}
	)

def get_events_request(request):
	if request.is_ajax():
		request_info = Request.objects.get(id=request.GET['id'])
		return render_to_response(
			'events/event_request_list.html',
			{
				'request_info' : request_info,
				'main_banner' : get_main_banner()
			}
		)		
	else:
		return HttpResponse('not ajax', mimetype="text/html")

def events_request(request):
	if request.is_ajax():
		# 세션 아이디와 post 아이디가 같은지 비교
		if request.session['user_id'] == request.POST['user_id']:
			user_info = Users.objects.get(user_id=request.session['user_id'])
		else:
			return HttpResponse('false', mimetype="text/html")
		
		event_info = Events.objects.get(id=request.POST['evt_id'])
		try:
			request_info = Request.objects.get(event=event_info, user=user_info)
			return HttpResponse('false', mimetype="text/html")
		except Request.DoesNotExist:
			comments = ''
			if 'comment' in request.POST:
				comments = request.POST['comment']
			else:
				comments = 'null'
				
			request_info = Request.objects.create(
				event=event_info,
				user=user_info,
				type=request.POST['type'],
				req_type='random',
				use_point=0,
				comment=comments,
				ip_addr=request.META['HTTP_X_REAL_IP'],
			)
			request_info.save()
			return HttpResponse(request_info.id, mimetype="text/html")
	else:
		return HttpResponse('not ajax', mimetype="text/html")

def events_delete(request):
	if request.is_ajax():
		if (request.session['user_id'] == request.POST['user_id']):
			user_info = Users.objects.get(user_id=request.session['user_id'])	
		else:
			return HttpResponse('false', mimetype="text/html")
		event_info =  Events.objects.get(id=request.POST['evt_id'])

		try:
			delete_info = Request.objects.get(event=event_info, user=user_info)	
			delete_info.delete()
			return render_to_response(
				'events/event_comment.html',
				{
					'view' : event_info,	
					'session': user_info
				}
			)
			
			
		except Request.DoesNotExist:
			return HttpResponse("false",mimetype="text/html")
	else:
		return HttpResponse("no ajax",mimetype="text/html")

