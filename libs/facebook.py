# -*- coding: utf-8 -*-
from BeautifulSoup import *
import urllib2
import urllib
from xml.dom import minidom
import simplejson
import facebook
import cgi

class FacebookAPI:
	Facebook_APPID = '236612713043774'
	Facebook_SECRET = 'fdf7709984eb31eb256c14d4dadc6acf'
	#Facebook_APPID = '443524122332344'
	#Facebook_SECRET = '7d1344fb3a095dd05c9bd0c537decd8a'
	
	def get_auth_url(self):
		url = 'http://www.facebook.com/dialog/oauth/?client_id='+self.Facebook_APPID+'&redirect_uri=https://inthe-movie.com/oauth_access/?facebook&scope=publish_stream,read_stream,offline_access&response_type=code'	
		return url
	
	def set_acc_token(self, code):
		args = dict(client_id=self.Facebook_APPID,redirect_uri='https://inthe-movie.com/oauth_access/?facebook')
		#args = dict(client_id=self.Facebook_APPID,redirect_uri='http://test.inthe-movie.com/oauth_access/?facebook')
		args["client_secret"] = self.Facebook_SECRET
		args["code"] = code
		response = cgi.parse_qs(urllib.urlopen("https://graph.facebook.com/oauth/access_token?"+urllib.urlencode(args)).read())
		try:
			access_token = response['access_token'][0]
			print access_token
		except Exception ,e:
			print "facebook TOKEN ERROR"
			print e
			print "====================="

		profile = simplejson.load(urllib.urlopen(
		                "https://graph.facebook.com/me?" +
		                urllib.urlencode(dict(access_token=access_token))))
		print profile, access_token
		return access_token, profile
	
	def get_profile(self, oauth_token):
		facebook_profile = urllib.urlopen(
	                "https://graph.facebook.com/me?" +
	                urllib.urlencode(dict(access_token=oauth_token))).read()
		return facebook_profile
	
	def post_wall(self, request, oauth_token, link):
		facebook_profile = simplejson.load(urllib.urlopen(
	                "https://graph.facebook.com/me?" +
	                urllib.urlencode(dict(access_token=oauth_token))))
		print facebook_profile
		#print facebook_profile.get('id')
		url = 'https://graph.facebook.com/me/feed'
		form = urllib.urlencode({	'access_token':oauth_token, 
									'message':(request.POST['content']).encode('utf-8'),
									'link':link
								})
		result = simplejson.load(urllib.urlopen(url, form))
		print result
		return result,facebook_profile
		