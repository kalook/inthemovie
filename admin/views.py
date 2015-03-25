# -*- coding: utf-8 -*-
from django.http import HttpResponse
from libs.lib import *
from django.http import HttpResponseRedirect
from club.models import *
from event.models import *
from admin.models import *
from movies.models import *
import os, os.path, sys
from libs.digg_pagination import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage
import simplejson
import urllib
import random
from django.conf import  settings
from django.template import RequestContext
from jinja2 import FileSystemLoader, Environment
from datetime import datetime

def check_admin(request):
	if request.session['is_admin'] == 'none':
		return HttpResponse('<script type="text/javscript">alert("access deined");history.go(-1);</script>')
	else:
		pass
		
def admin_main(request):
	check_admin(request)

	return render_to_response(
		'admin/index.html',
		{
			'request' : request,
			'user' : request.user,
			'session' : request.session	
		}
	)

def memeber_panalty(request, id=0):
	member = Users.objects.get(id=id)
	panlty = Panalty.objects.create(
		user = member,
		reason = 'a',
		start_date = '2012-01-01',
		end_date = '2112-12-31',
		ip_addr = request.META['REMOTE_ADDR']
	)
	return HttpResponse('true')

def member_manage_panalty(request):
	check_admin(request)
	panalties = Panalty.objects.all()
	return render_to_response(
	'admin/member_block.html',
		{
			'request' : request,
			'user' : request.user,
			'session' : request.session,
			'panalties' : panalties

		}
    )	

def panalty_delete(request, id=0):
	panalty = Panalty.objects.get(id=id)
	panalty.delete()
	return HttpResponseRedirect('/inthe-movie/admin/member/block/')

def member_manage(request):
	check_admin(request)
	page = 1
	if 'page' in request.GET:
		page = request.GET['page']
	
	member_info = []

	if 'search_type' in request.GET:
		if request.GET['search_type'] == 'user_id':
			member_info = Users.objects.filter(user_id__contains = request.GET['keyword']).order_by('-id')
		elif request.GET['search_type'] == 'name':
			member_info = Users.objects.filter(name__contains = request.GET['keyword']).order_by('-id')
		elif request.GET['search_type'] == 'nick_name':
			member_info = Users.objects.filter(nick_name__contains = request.GET['keyword']).order_by('-id')
		else:
			member_info = Users.objects.order_by('-id')
	else:
		member_info = Users.objects.order_by('-id')

	print member_info
	paginator = Paginator(member_info, 20)

	try:
		member_info = paginator.page(page)
	except (EmptyPage, InvalidPage):
		member_info = paginator.page(paginator.num_pages)
	
	digg = digg_pagination(paginator.page(page))
	
	return render_to_response(
	'admin/member.html',
		{
			'request' : request,
			'user' : request.user,
			'session' : request.session,
			'member_info' : member_info,
			'page'  : page,
			'digg' : digg
		}
    )

def member_manage_view(request):	
	check_admin(request)
	#member_info = Users.objects.get(id=request.GET['id'])
	if request.method=="POST":
		member_info = Users.objects.get(id=request.POST['id'])
		if request.POST['password']:
			member_info.password = hashlib.md5(request.POST['password']).hexdigest()
		member_info.name = request.POST['name']
		member_info.nick_name = request.POST['nick_name']
		member_info.mobile_phone = request.POST['mobile_phone']
		member_info.email = request.POST['email']
		member_info.save()
		
	else:
		member_info = Users.objects.get(id=request.GET['id'])

	return render_to_response(
	'admin/member_view.html',
		{
			'request' : request,
			'user' : request.user,
			'session' : request.session,
			'member_info' : member_info
		}
    )	

def event_manage(request):
	check_admin(request)
	if 'stat' in request.GET:
		event_info = Events.objects.filter(status=request.GET['stat'])
	else:
		event_info = Events.objects.filter(status='start')
	return render_to_response(
		'admin/event.html',
		{
			'request' : request,
			'user' : request.user,
			'session' : request.session,
			'event_list' : event_info,
		}
	) 
	
def event_manage_view(request, idx):
	check_admin(request)
	view_info = Events.objects.get(id=idx)

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

	if 'csv' in request.GET:
		import csv
		get_date = datetime.now().strftime("%Y-%m-%d")
		response = HttpResponse(mimetype='text/csv')
		response['Content-type'] = 'charset=euc-kr'
		response['Content-Disposition'] = 'attachment; filename=event_request_'+get_date+'.csv'
		if view_info.comment_type == 'T':
			writer = csv.writer(response)
			writer.writerow(['name','name1','nick_name', 'user_id', 'date', 'mobile_phone','mobile_phone1', 'comment','ip'])
			for request in req_list:
				if request.req_location == 'facebook':
					fb = (request.comment).split('/')
					writer.writerow([fb[2].encode('euc-kr'), fb[2].encode('euc-kr'), 
									fb[2].encode('euc-kr'), fb[0].encode('euc-kr'), 
									request.req_date, fb[1].encode('euc-kr'),fb[1].encode('euc-kr'),
									request.comment.encode('euc-kr'), request.ip_addr.encode('euc-kr')])					
				else:
					s_name = request.user.name
					if len(s_name) == 2:
						s_name = s_name[0] + 'O'
					elif len(s_name) == 4:
						s_name = s_name[0] + 'OO' + s_name[3]
					else:
						s_name = s_name[0] + 'O' + s_name[2]

					hp = ((request.user.mobile_phone).replace('-','')).replace(' ','')
					hp1 = ''
					hp2 = ''
					if len(hp) == 10:
						hp1 = hp[:3] + '-***-' + hp[6:]
						hp2 = hp[:3] + '-' + hp[3:6] + '-' + hp[6:]
					else:
						hp1 = hp[:3] + '-****-' + hp[7:]
						hp2 = hp[:3] + '-' + hp[3:7] + '-' + hp[7:]
					writer.writerow([request.user.name.encode('euc-kr'), s_name.encode('euc-kr'), 
									request.user.nick_name.encode('euc-kr'),request.user.user_id.encode('euc-kr'), 
									request.req_date, hp2.encode('euc-kr'), hp1.encode('euc-kr'), request.comment.encode('euc-kr'),
									request.ip_addr.encode('euc-kr')])			
		else:
			writer = csv.writer(response)
			writer.writerow(['name','nick_name', 'user_id', 'date', 'mobile_phone'])
			for request in req_list:
				writer.writerow([request.user.name.encode('euc-kr'), request.user.nick_name.encode('euc-kr'), 
								request.user.user_id.encode('euc-kr'), request.req_date, request.user.mobile_phone, request.ip_addr.encode('euc-kr')])
		return response
	else:
		return render_to_response(
			'admin/event_view.html',
			{
				'request' : request,
				'user' : request.user,
				'session' : request.session,
				'view' : view_info,
			'request_list' : req_list,
			'req_count' : req_count
			}
		)	

def event_manage_edit(request, idx):
	check_admin(request)
	event = Events.objects.get(id=idx)
	if request.method == 'POST':	
		thum_image = event.thumnail_image
		main_image = event.main_image
		
		movie_info = None
		
		if 'is_del1' in request.POST:
			if request.FILES['thumnail_image']:
				thum_image = handle_uploaded_file('events',request.FILES['thumnail_image'])

		if 'is_del2' in request.POST:
			if request.FILES['main_image']:
				main_image = handle_uploaded_file('events',request.FILES['main_image'])
		
		
		if 'hotmovie_id' in request.POST:
			movie_info = Movies.objects.get(id=int(request.POST['hotmovie_id']))
			
		event.movie = movie_info
		event.type = request.POST['type']
		event.req_type = request.POST['req_type']
		event.movie_title = request.POST['movie_title']
		event.thumnail_image = thum_image
		event.main_image = main_image
		if  'vod_url' in request.POST:
			event.vod_url = request.POST['vod_url']
		event.subject = request.POST['subject']
		event.date = request.POST['evt_date']
		event.place = request.POST['place']
		event.people = request.POST['people']
		event.people_count = request.POST['people_count']
		event.announce = request.POST['announce']
		event.main_content = request.POST['ir1']
		event.rule_content = request.POST['ir2']
		event.status = request.POST['status']
		event.comment_type = request.POST['comment_type']
		event.ip_addr = request.META['REMOTE_ADDR']
		event.save()
		
		return HttpResponseRedirect('/inthe-movie/admin/event/view/'+str(event.id))
	else:
		return render_to_response(
			'admin/event_edit.html',
			{	
				'request' : request,
				'user' : request.user,
				'session' : request.session,
				'view' : event,
			}
		)
	
def event_manage_delete(request, idx):
	check_admin(request)
	event = Events.objects.get(id=idx)
	event.delete()
	return HttpResponseRedirect('/inthe-movie/admin/event')

def event_manage_copy(request, idx):
	check_admin(request)
	event = Events.objects.get(id=idx)

	copy_event = Events.objects.create(
			user = event.user,
			type = event.type,
			req_type = event.req_type,
			movie = event.movie,
			movie_title = event.movie_title,
			subject = event.subject,
			thumnail_image = event.thumnail_image,
			main_image = event.main_image,
			vod_url = event.vod_url,
			date = event.date,
			place = event.place,
			people = event.people,
			people_count = event.people_count,
			announce = event.announce,
			main_content = event.main_content,
			rule_content = event.rule_content,
			status = 'closed',
			comment_type = event.comment_type,
			ip_addr = event.ip_addr
	)
	return HttpResponseRedirect('/inthe-movie/admin/event/edit/'+str(copy_event.id)+'/')


def handle_uploaded_file(paths,f):
	upload_path = settings.STORAGE_PATH+'/'+paths
	
	gen_name = GenPasswd()
	tmp_filename = (f.name).split('.')
	file_ext = tmp_filename[1]
	gen_file_name = datetime.now().strftime('%Y_%m_%d') + '_' + (gen_name) + '.' + file_ext
	if not os.path.exists(upload_path):
		os.makedirs(upload_path)    
	#gen_file_name = datetime.now().strftime('%Y_%m_%d') + '_' + (f.name)
	destination_path = upload_path+'/%s' % gen_file_name
	destination = open(destination_path, 'wb+')

	for chunk in f.chunks():
		destination.write(chunk)
	destination.close()
	return gen_file_name

def hotmovie_select(request):
	movies_list = Movies.objects.filter(is_collected='T').order_by('-show')
	return render_to_response(
		'admin/hotmovie_select.html',
		{	
			'request' : request,
			'user' : request.user,
			'session' : request.session,
			'movies_list' : movies_list
		}
	)	

def event_create(request):
	check_admin(request)
	if request.method == 'POST':	
		user_info = Users.objects.get(user_id=request.session['user_id'])

		movie_info = main_image = vod_url = None
		if request.POST['req_type'] == 'normal':
			main_image = handle_uploaded_file('events',request.FILES['main_image'])
			vod_url = request.POST['vod_url']
			
		elif request.POST['req_type'] == 'social':
			movie_info = Movies.objects.get(id=int(request.POST['hotmovie_id']))

		thum_image = handle_uploaded_file('events',request.FILES['thumnail_image'])

		event = Events.objects.create(
			user = user_info,
			type = request.POST['type'],
			req_type = request.POST['req_type'],
			movie = movie_info,
			movie_title = request.POST['movie_title'],
			subject = request.POST['subject'],
			thumnail_image = thum_image,
			main_image = main_image,
			vod_url = vod_url,
			date = request.POST['evt_date'],
			place = request.POST['place'],
			people = request.POST['people'],
			people_count = request.POST['people_count'],
			announce = request.POST['announce'],
			main_content = request.POST['ir1'],
			rule_content = request.POST['ir2'],
			status = request.POST['status'],
			comment_type = request.POST['comment_type'],
			ip_addr = request.META['REMOTE_ADDR']
		)
		return HttpResponseRedirect('/inthe-movie/admin/event/')
	else:

		return render_to_response(
			'admin/event_create.html',
			{	
				'request' : request,
				'user' : request.user,
				'session' : request.session
			}
		)


    
def club_manage(request):
	check_admin(request)
	boards = Boards.objects.all()
	return render_to_response(
	'admin/club.html',
	{
			'request' : request,
			'user' : request.user,
			'session' : request.session,
			'boards' : boards
		}
    )
    
def club_create(request):
    check_admin(request)
    if request.method == 'POST':
        board = Boards.objects.create(
                title = request.POST['title'],
                code = request.POST['code'],
                type = request.POST['type']
        )
        return HttpResponseRedirect('/inthe-movie/admin/club/')
 
    return render_to_response(
        'admin/club_create.html',
        {
			'request' : request,
        	'user' : request.user,
        	'session' : request.session
		}
    )

def email_manage(request):
	check_admin(request)
	email_info = Emails.objects.all().order_by("-id")
	if request.method == 'POST':
		user = Users.objects.get(user_id = request.session['user_id'])
		board = Emails.objects.create(
				user = user,
				title = request.POST['subject'],
				content = request.POST['ir1'],
				is_send = request.POST['is_send'],
				ip = request.META['REMOTE_ADDR']
        )	
		return HttpResponseRedirect('/inthe-movie/admin/email/')
		
	return render_to_response(
		'admin/email.html',
		{
			'request' : request,
			'user' : request.user,
			'session' : request.session,
			'email_info' : email_info
		}
	)	


def email_manage_view(request):
	check_admin(request)
	email_id = request.GET['id']
	email_info = Emails.objects.get(id=email_id)
	if request.method == 'POST':
		email_info.title = request.POST['subject']
		email_info.content = request.POST['ir1']
		email_info.is_send = request.POST['is_send']
		email_info.save()

		return HttpResponseRedirect('/inthe-movie/admin/email/')
	
	return render_to_response(
		'admin/email_view.html',
		{
			'request' : request,
			'user' : request.user,
			'session' : request.session,
			'email_info' : email_info
		}
	)
	
def hotmovie_manage(request):
	check_admin(request)
	if request.method == 'POST':
		movie = Movies.objects.get(id=request.POST['hotmovie_id'])
		movie.show = request.POST['hotmovie_type']
		movie.save()
		print request.POST
		return HttpResponseRedirect('/inthe-movie/admin/hotmovie/')

	movies_list = Movies.objects.filter(is_collected='T').order_by('-show')
	return render_to_response(
		'admin/hotmovie_manage.html',
		{
			'request' : request,
			'user' : request.user,
			'session' : request.session,
			'movies_list' : movies_list
		}
	)	
  
def banner(request):
    
    check_admin(request)
    print "오늘 날짜는 : ",datetime.now()
    banner_List = Banner.objects.order_by('-id')
            
    if request.method =='POST':
        operate = Banner.objects.create(
            link = request.POST['link'],
            position = request.POST['position'],
            blank = request.POST['blank'],
            start_date = request.POST['start_date'],
            last_date = request.POST['end_date'],
            banner_root =  handle_uploaded_file('/banner_files',request.FILES['upload'])
        )
        operate.save()
        return HttpResponseRedirect('')
        
    return  render_to_response(
       'admin/banner.html',
       {
            'request' : request,
            'banner_List' : banner_List,
            'user' : request.user,
			'session' : request.session
        }
                               )

def banner_edit(request, idx):
    check_admin(request)
         
    banner_List = Banner.objects.order_by('-id')
    banner = Banner.objects.get(id=idx)
    if request.method == 'POST':
        banner.link = request.POST['link']
        banner.position = request.POST['position']
        banner.blank = request.POST['blank']
        banner.start_date = request.POST['start_date']
        banner.last_date = request.POST['end_date']
    #    if request.FILES['upload']==True:
        try:
            if request.FILES['upload']:
                banner.banner_root = handle_uploaded_file('/banner_files',request.FILES['upload'])
        except:
            print "no files"
        banner.save()
        return HttpResponseRedirect('/inthe-movie/admin/ad')
   
    return render_to_response(
      'admin/banner_edit.html',
      {
            'request' : request,
            'banner' : banner,
           # 'main_banner' : get_main_banner(),
            'banner_List' : banner_List,
            'user' : request.user,
			'session' : request.session
       }
                              )

	
     
def banner_delete (request, idx):
  #  print idx
    banner = Banner.objects.get(id=idx)
    banner.delete()
    return HttpResponseRedirect('/inthe-movie/admin/ad')

