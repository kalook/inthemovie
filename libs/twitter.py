# -*- coding: utf-8 -*-
import tweepy
from BeautifulSoup import *
import urllib2
import urllib
from xml.dom import minidom
import simplejson

class TwitterAPI:
	CONSUMER_KEY = 'lhNPjTU2n7zDxRGUeEQEw'
	CONSUMER_SECRET = 'iX1x866fiYrWiW6TOSf5CilU9ZRPyrbIVf2AHYFj8'

	#CONSUMER_KEY = 'OI24PNUR6vtykgxx8VpLlw'
	#CONSUMER_SECRET = 'GoURPS5MsBQGLtrXk3H8MMTc9ZrpBjaZiHzKpMPA7yE'
	
	def get_auth_url(self,request):
		auth = tweepy.OAuthHandler(self.CONSUMER_KEY, self.CONSUMER_SECRET)
		try:
			redirect_url = auth.get_authorization_url()
			request.session['request_token'] = auth.request_token.key+"|"+auth.request_token.secret
		except tweepy.TweepError:
		    print 'Error! Failed to get request token.'
		return redirect_url
		
	def set_access_token(self, request):
		auth = tweepy.OAuthHandler(self.CONSUMER_KEY, self.CONSUMER_SECRET)
		request_token = (request.session['request_token']).split('|')
		auth.set_request_token(request_token[0], request_token[1])
		try:
		    auth.get_access_token(request.GET['oauth_verifier'])
		except tweepy.TweepError:
		    print 'Error! Failed to get access token.'
		return auth
	
	def get_connection(self, oauth_token):
		auth = tweepy.OAuthHandler(self.CONSUMER_KEY, self.CONSUMER_SECRET)
		access_token = oauth_token.split('|')
		auth.set_access_token(access_token[0], access_token[1])
		api = tweepy.API(auth)
		return api
		
	def tweet(self, request, oauth_token, url):
		api = self.get_connection(oauth_token)
		#print request.POST['content'] , url
		result = api.update_status((request.POST['content']+' '+url).encode('utf-8'))
		#print u'인증성공' ,result
		print api.me()
		return result, api.me()
		