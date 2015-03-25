# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from member.models import *
from movies.models import *
from event.models import *
from club.models import *
from sns.models import *
from libs.lib import *
from libs.api_request import *
from django.http import HttpResponse
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
from libs.me2day import *
from libs.twitter import *
from libs.facebook import *

max_age = 365*24*60*60 
expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")


def oauth(request):
	url = 'none'
	if 'HTTP_REFERER' in request.META:
		request.session['oauth_redirect_url'] = request.META['HTTP_REFERER']

	if 'me2day' in request.GET:
		me2day = Me2dayAPI()
		url = me2day.get_auth_url()

	elif 'twitter' in request.GET:
		twitter = TwitterAPI()
		url = twitter.get_auth_url(request)
		
	elif 'facebook' in request.GET:
		facebook = FacebookAPI()
		url = facebook.get_auth_url()
	
	return HttpResponseRedirect(url)
	
def oauth_access(request):
	#요청URL 리셋
	request.session['oauth_redirect_url'] = request.session['oauth_redirect_url'].split('?')[0]
	if 'me2day' in request.GET:
		print request.GET
		if 'token' in request.GET:
			print 'where is the token?'
			user_id = request.GET['user_id']
			token = request.GET['token']
			user_key = request.GET['user_key']
			try:
				user_info = Users.objects.get(user_id=request.session['user_id'])
				sns_info = Sns.objects.create(
					user = user_info,
					service = 'me2day',
					oauth_token = user_id+'|'+token+'|'+user_key
				)
				response = HttpResponseRedirect(request.session['oauth_redirect_url'])
			except:
				print "create_cookie"
				response = HttpResponseRedirect(request.session['oauth_redirect_url'])
				response.set_cookie('oauth_me2day', user_id+'|'+token+'|'+user_key, max_age=max_age, expires=expires)
				print response
			request.session['oauth_SNS'] = 'me2day'
		else:
			return HttpResponseRedirect('/oauth?me2day')
	elif 'twitter' in request.GET:
		if 'oauth_token' in request.GET:
			twitter = TwitterAPI()
			auth = twitter.set_access_token(request)
			api = tweepy.API(auth)
			print "twitter API"
			try:
				user_info = Users.objects.get(user_id=request.session['user_id'])
				sns_info = Sns.objects.create(
					user = user_info,
					service = 'twitter',
					oauth_token = auth.access_token.key+'|'+auth.access_token.secret
				)
				response = HttpResponseRedirect(request.session['oauth_redirect_url'])
				print "redirect URL : ",request.session['oauth_redirect_url']
			except:
				print "create_cookie"
				response = HttpResponseRedirect(request.session['oauth_redirect_url'])
				response.set_cookie('oauth_twitter', auth.access_token.key+'|'+auth.access_token.secret, max_age=max_age, expires=expires)
				print response
			request.session['oauth_SNS'] = 'twitter'
		else:
			return HttpResponseRedirect('/oauth?twitter')
	elif 'facebook' in request.GET:
		facebook = FacebookAPI()
		if 'code' in request.GET:
			access_token, profile = facebook.set_acc_token(request.GET['code'])
			try:
				user_info = Users.objects.get(user_id=request.session['user_id'])
				sns_info = Sns.objects.create(
					user = user_info,
					service = 'facebook',
					oauth_token = access_token
				)
				response = HttpResponseRedirect(request.session['oauth_redirect_url'])
			except:
				# 쿠키생성
				print "create_cookie"
				response = HttpResponseRedirect(request.session['oauth_redirect_url'])
				response.set_cookie('oauth_facebook', access_token, max_age=max_age, expires=expires)
				print response
			request.session['oauth_SNS'] = 'facebook'
		else:
			return HttpResponseRedirect('/oauth?facebook')
	#return HttpResponseRedirect(request.session['oauth_redirect_url'])
	return response

def get_sns_data(request):
	if request.POST.has_key('service'):
		try:
			user_info = Users.objects.get(user_id=request.session['user_id'])
			sns_info = Sns.objects.get(user=user_info,service=request.POST['service'])
			oauth_token = sns_info.oauth_token
		except:
			oauth_token = request.COOKIES['oauth_'+request.POST['service']]
			
		if request.POST['service'] == 'facebook':
			facebookAPI = FacebookAPI()
			facebook_profile = facebookAPI.get_profile(oauth_token)
			return HttpResponse(facebook_profile)
			
		elif request.POST['service'] == 'me2day':
			me2day = Me2dayAPI()
			me2day_profile = me2day.get_profile(oauth_token)
			return HttpResponse(me2day_profile)
			
		elif request.POST['service'] == 'twitter':
			twitter = TwitterAPI()
			api = twitter.get_connection(oauth_token)
			print api.me().profile_image_url
			return HttpResponse(api.me().profile_image_url)
	else:
		return HttpResponse("false")
		
def sns_logout(request):
	response = HttpResponse('delete_cookie')
	request.session['oauth_SNS'] =''
	if request.POST.has_key('service'):
		if request.session.has_key('user_id'):
			print "delete Cookie"
			response.delete_cookie(key=str('oauth_'+request.POST['service']))
			return response
		else:
			print request.POST['service'] , "delete!!!!!!!"
			response.delete_cookie(key=str('oauth_'+request.POST['service']))
			return response
	else:
		return HttpResponse("false")
	
def sns_post(request):
	username = link = profile_image = None
	email = 'null'
	if request.POST.has_key('service'):
		movie_info = Movies.objects.get(id=request.POST['movie_id'])
		url = "https://inthe-movie.com/"+movie_info.title_url+'/vlaah'
		
		try:
			user_info = Users.objects.get(user_id=request.session['user_id'])
			sns_info = Sns.objects.get(user=user_info,service=request.POST['service'])
			oauth_token = sns_info.oauth_token
		except:
			oauth_token = request.COOKIES['oauth_'+request.POST['service']]
		
		if request.POST['service'] == 'facebook':
			print oauth_token
			facebook = FacebookAPI()
			result,profile = facebook.post_wall(request, oauth_token, url)
			username = profile.get('name')
			profile_image = 'http://graph.facebook.com/'+profile.get('id')+'/picture/'
			param = (str(result.get('id'))).split('_')
			link = 'http://www.facebook.com/permalink.php?story_fbid='+param[1]+'&id='+param[0]
			
		elif request.POST['service'] == 'me2day':
			print "me2dayPOST :  ",oauth_token
			me2dayAPI = Me2dayAPI()
			profile = simplejson.load(me2dayAPI.get_profile(oauth_token))
			profile_image = profile.get('face')
			result = me2dayAPI.post(request, oauth_token, url, movie_info)
			username,link,email = result.get('author').get('nickname'), result.get('permalink'), profile.get('email')

		elif request.POST['service'] == 'twitter':
			param =  urllib.urlencode({
						'login' : 'toychair',
						'apiKey' : 'R_5611dd1857a105845f3cd1e7dac5efd5',
						'longUrl' : url,
						'format' : 'json'
					})
			shorten = simplejson.load(urllib.urlopen('http://api.bitly.com/v3/shorten'+'?'+param))			
			twitterAPI = TwitterAPI()
			result, profile = twitterAPI.tweet(request, oauth_token, shorten.get('data').get('url'))
			profile_image = profile.profile_image_url
			username,link = profile.screen_name, 'http://twitter.com/'+profile.screen_name+'/status/'+str(result.id)
		
		comment = SocialComment.objects.create(
			movie = movie_info,
			content = request.POST['content'],
			email = email,
			username = username,
			link = link,
			service = request.POST['service'],
			profile_image = profile_image
		)
		
		comment_list = movie_info.socialcomment_set.filter(id__gt = comment.id-1).order_by('-id')
		return render_to_response(
			'movies/hotmovie_vlaah_list.html',
			{
				'request' : request,
				'comment_list' : comment_list,
				'post' : 'true'
			}
		)
	else:
		return HttpResponse("false")
		
def poster(request):
	if 'q' in request.GET:
		result = urllib.urlopen(request.GET['q']).read()
		return HttpResponse(result)
	else:
		return HttpResponse('false')
	