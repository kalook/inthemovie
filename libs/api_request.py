# -*- coding: utf-8 -*-
from BeautifulSoup import *
import urllib2
import urllib
from xml.dom import minidom
import simplejson
import feedparser

class NaverAPI:
	NAVERKEY = 'b4067652f9a61ab0cb627512557442a6'
	URL = 'http://openapi.naver.com/search'
	search_url = 'http://openapi.naver.com/search?key='+NAVERKEY+'&target=ranktheme&query=movie'
	
	#네이버 상영중영화, 상영예정영화 
	def get_naver_movie(self, type):
		url = 'http://movie.naver.com/movie/running/%s.nhn' % type
		articles = []
		handle = urllib2.urlopen(url)
		data = handle.read()
		soup = BeautifulSoup(data, fromEncoding="euc-kr")
		article = soup.findAll(['h5'])
		print article
		for item in article:
			articles.append(str(item('a')[0].string).decode("utf-8"))
		return articles	
		
	#네이버 실시간 검색어
	def get_search_keyword(self, target, keyword):
		lists = []
		dom  = self.setReq(target, keyword)
		items = dom.getElementsByTagName("K")

		for item in items:
			lists.append(item.childNodes[0].nodeValue)
		return lists	

	def getText(self, nodelist):
		rc = ""
		for node in nodelist:
			if node.nodeType == node.TEXT_NODE:
				rc = rc + node.data

		return rc.encode("utf-8")

	def getItem(self, nodelist):
		items = {}
		for node in nodelist:
			items[node.tagName] = self.getText(node.childNodes)
		return items

	def getItemList(self, data):
		items = data.getElementsByTagName("channel")[0].getElementsByTagName("item")
		total = data.getElementsByTagName("channel")[0].getElementsByTagName("total")
		total_count = 0
		for to in total:
			total_count = to.childNodes[0].nodeValue
		itemlist = {}
		for i, item in enumerate(items):
			itemlist[i] = self.getItem(item.childNodes)
		return itemlist, total_count
	
	def setReq(self, target, keyword):
		form = {"key": self.NAVERKEY,
				"query": keyword,
				"target":target,
				"display":"100"}
		form = urllib.urlencode(form)
		dom = minidom.parse(urllib.urlopen(self.URL+'?'+form))
		return 	dom	
	
	def getAPI(self, target, keyword):
		dom  = self.setReq(target, keyword)
		itemlist, total_count = self.getItemList(dom);

		return itemlist, total_count
	
class DaumAPI:
	DAUMKEY = '68790bb1350c92f6aa1bf376f61184a4149611de'
	DAUMSEARCHKEY = 'e981006b4dd255000917546d4b15f0803d244c74'
	URL = 'http://apis.daum.net/'
	VIEW_URL = 'http://api.v.daum.net/open/news_list.xml'
	
	def getAPI(self, config):
		url = self.URL + '%s/%s' % (config.get("type"),config.get("service"))

		if config.get("type") == "search":
			key = self.DAUMSEARCHKEY
		else:
			key = self.DAUMKEY
		form = {"apikey": key,
				"output": "json",
				"result" : "20",
				"sor" : "recency",
				"q": config.get("q")}
		
		services = config.get("service")
		if services == 'movie':
			form = urllib.urlencode(form) + '&result=1'
		else:
			form = urllib.urlencode(form) 
		result = simplejson.load(urllib.urlopen(url+'?'+form))	
		return result
		
	def getViewAPI(self, q):
		url = self.VIEW_URL
		
		form = {"list_type" : "best","q":q}
		form = urllib.urlencode(form)
		result = urllib.urlopen(url+'?'+form).read()
		#soup = BeautifulSoup(result, fromEncoding="euc-kr")
		result = result.replace('encoding="euc-kr"', 'encoding="utf-8"',1)
		result = unicode(result, 'euc-kr').encode('utf-8')
		dom = minidom.parseString(result)
		return dom
	
	def getDaumRating(self, url):
		#print url
		datas = urllib2.urlopen(url).readlines()
		rating_lists = []
		for data in datas:
			soup = BeautifulSoup(data)
			result = soup.find('em')
			if result:
				rating_lists.append(result.string)
			else:
				pass
		for check in rating_lists:
			try:
				if check>-1:
					return check
					break
			except Exception as e:
				print e
	
		#return rating_lists[2]

	#다음 상영예정영화, 현재상영영화
	def get_daum_movie(self, type):
		url = ''
		if type == 'pre_movie':
			url = 'http://movie.daum.net/movieinfo/coming/movieInfoScheduled.do?modeType=day&order=recently'
		elif type == 'curr_movie':
			url = 'http://movie.daum.net/movieinfo/now/movieinfoReleased.do?modeType=all&order=recently'
		articles = []
		handle = urllib2.urlopen(url)
		data = handle.read()
		soup = BeautifulSoup(data, fromEncoding="utf-8")
		article = soup.findAll('span',{ "class" : "img"})
		for aa in article:
			sets = {}
			page = BeautifulSoup(str(aa))
			for attr, value in page.find('a').attrs:
				sets[attr] = value
			articles.append(sets)
		return articles

class inthemovieNotice:
	URL = 'http://blog.inthe-movie.com/rss'
	posts = None
	def getNotice(self):
		try:
			d = feedparser.parse(self.URL)
			posts = d.entries
		except Exception, e:
			print e
		return posts
	
class m2dayAPI:
	url = 'http://me2day.net/search.json?query=('
	url2 = ')&search_at=all'
	def get_data(self,title):
		form = {"t":title}
		form = urllib.urlencode(form)
		result = simplejson.load(urllib.urlopen(self.url + form + self.url2))
		return result
	
class imdbAPI:
	#URL = 'http://www.deanclatworthy.com/imdb/'
	URL = 'http://www.imdbapi.com/'
	def get_imdb_data(self, title):
		form = {"t": title}
		#form = {"q": title}
		form = urllib.urlencode(form)
		result = simplejson.load(urllib.urlopen(self.URL+'?'+form))	
		return result

class movistAPI:
	URL ='http://www.movist.com/json_main/inthe_movie.asp?title='
	def get_movist_data(self, title):
		result = simplejson.load(urllib.urlopen(self.URL + title.encode('utf-8')))
		return result
	
		
		
		
		
