# -*- coding: utf-8 -*-
from BeautifulSoup import *
import urllib2
import urllib
from xml.dom import minidom
import simplejson
import hashlib
import random

class Me2dayAPI:
	Me2day_APPLICATION_KEY = '9ddae7f096203ad1134f57af2ce6de24'
	#Me2day_APPLICATION_KEY = '2a85c5403e79b46492adb67c7402b462'
	def get_auth_url(self):
		
		url = 'http://me2day.net/api/get_auth_url.json'
		form = { 'akey' : self.Me2day_APPLICATION_KEY }
		form = urllib.urlencode(form)
		result = simplejson.load(urllib.urlopen(url+'?'+form))	
		print result
		return result.get("url")
		
	def get_profile(self, oauth_token):
		me2day_cookie = oauth_token.split('|')
		url = 'http://me2day.net/api/get_person/%s.json' % me2day_cookie[0]
		result = urllib.urlopen(url)
		return result
	
	def post(self, request, oauth_token, link, movie_info):
		me2day_cookie = oauth_token.split('|')
		url = 'http://me2day.net/api/create_post/%s.json' % me2day_cookie[0]

		md5 = hashlib.md5()
		nonce = '%08x' % random.randint(0, 16 ** 8 - 1) 
		md5.update(nonce + me2day_cookie[2])
		ukey = nonce + md5.hexdigest()
		content = '['.encode('utf-8')+movie_info.title_kor.encode('utf-8')+' ] '.encode('utf-8') + request.POST['content'].encode('utf-8')
		form = urllib.urlencode(
			{ 
				'akey'	:	self.Me2day_APPLICATION_KEY, 
				'uid' : me2day_cookie[0],
				'ukey' : ukey,
				'post[body]'	:	content,
				'post[tags]'	: '인더무비 이벤트 '+movie_info.title_kor.encode('utf-8')
			}
		)
		result = simplejson.load(urllib.urlopen(url+'?'+form))
		print self.Me2day_APPLICATION_KEY , me2day_cookie[0], ukey, content, movie_info.title_kor.encode('utf-8')
		print result.get('code'), result.get('description')
		return result 
		