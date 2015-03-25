# -*- coding: utf-8 -*-
from django.http import HttpResponse
from datetime import datetime
from libs.lib import *
from django.http import HttpResponseRedirect
from event.models import *
import simplejson

def api_event_list(request):
    event_info = Events.objects.filter(status__in=['start']).order_by('-id')
    lists = []
    for event in event_info:
        attr = {}
        attr['id'] = event.id
        attr['movie_title'] = event.movie_title
        attr['image'] = 'https://inthe-movie.com/files/events/'+str(event.thumnail_image)
        attr['date'] = event.date
        attr['place'] = event.place
        lists.append(attr)

    json = simplejson.dumps(lists, sort_keys=True, indent=4)
    return HttpResponse(json)

def api_event_view(request, id):
    event_info = Events.objects.get(id=id)
    attr = {}
    attr['id'] = event_info.id
    attr['movie_title'] = event_info.movie_title
    attr['main_content'] = event_info.main_content
    attr['thumnail_image'] = 'https://inthe-movie.com/files/events/'+str(event_info.main_image)
    attr['vod_url'] = event_info.vod_url
    attr['date'] = event_info.date
    attr['place'] = event_info.place
    attr['people'] = event_info.people
    attr['announce'] = event_info.announce
    attr['type'] = event_info.type

    json = simplejson.dumps(attr, sort_keys=True, indent=4)
    return HttpResponse(json)

def api_event_request(request):
    key = "48bf71459d0cf22838e51fe636abac75"
    api_key = request.POST['api_key']
    user_id = int(request.POST['fb_id'])
    event_id = int(request.POST['event_id'])
    type = request.POST['type']
    comments = request.POST['comments']

    if key != api_key:
        response = HttpResponse('not access api key')
        response['Access-Control-Allow-Origin']  = '*'
        return response

    exist = Request.objects.filter(event=int(event_id), comment=comments)
    try:
        if exist[0].id:
            return HttpResponse('exist')
    except Exception, e:
        pass

    ipaddr = ''
    if 'HTTP_X_REAL_IP' in request.META:
        ipaddr = request.META['HTTP_X_REAL_IP']
    else:
        ipaddr = request.META['REMOTE_ADDR']

    try:
        event = Events.objects.get(id=event_id)
        request_info = Request.objects.create(
            event=event,
            type=type,
            req_type='random',
            use_point=0,
            req_location='facebook',
            comment=comments,
            ip_addr=request.META['HTTP_X_REAL_IP'],
        )
        request_info.save()
    except Exception, e:
        response = HttpResponse(e)
        response['Access-Control-Allow-Origin']  = '*'
        return response

    response = HttpResponse('true')
    response['Access-Control-Allow-Origin']  = '*'
    return response
