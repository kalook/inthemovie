# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
import simplejson
from xml.dom import minidom
from libs.api_request import *
from movies.models import *
import time
import urllib 
from cStringIO import StringIO 
import Image
class Command(BaseCommand):
	# 언어환경
	LANG = "utf-8"
	naver = NaverAPI()
	daum = DaumAPI()
	imdb = imdbAPI()
	movist = movistAPI()
	#네이버 실시간 검색 - 영화
	
	args = '<poll_id poll_id ...>'
	help = 'Closes the specified poll for voting'
	
	def handle(self, *args, **options):
		t = time.time()

		movie_list = Movies.objects.filter(is_collected = 'T')
		
		for movie in movie_list:
			title_eng = link_naver = thumnail = link_imdb = ''
			rating_naver = rating_daum = rating_imdb = rating_movist = 0		
			
			title = movie.title_kor
			title_api = '영화' + movie.title_kor.encode('utf-8')
			
			try:
				print title.encode("utf-8")
			except:
				pass				

			#네이버 영화 기본정보
			naver_api,movie_count = self.naver.getAPI('movie',title.encode("utf-8"))
			if naver_api:
				
				title_eng = naver_api[0].get('subtitle')
				rating_naver = naver_api[0].get('userRating')
				link_naver = naver_api[0].get('link')
				try:
					print u'네이버평점 수집완료 : ' , rating_naver
				except:
					pass
			#다음 영화 기본정보
			#daum_movie_api = self.daum.getAPI({"type":"contents","service":"movie","q":title.encode("utf-8")})
			#if daum_movie_api:
			#	item = daum_movie_api['channel']	
			#	contents = item['item']
			#	for content in contents:
			#		for row in content['title']:
			#			link_daum = row.get('link')
			#			rating_daum = self.daum.getDaumRating(row.get('link'))
			if movie.link_daum:
				rating_daum = self.daum.getDaumRating(movie.link_daum)
				try:
					print u'다음평점 수집완료 : ' , rating_daum
				except:
					pass

			else:
				rating_daum = 0	
			
			# movist 정보 
			try:
				movist_api = self.movist.get_movist_data(title)
				if movist_api.get('state') =='N':
					rating_movist =0
				else:
					rating_movist = movist_api.get('average')
				try:
					print u'무비스트 API: ' , movist_api
					print u'무비스트평점 수집완료: ' , rating_movist
				except:
					pass

				
			except Exception as e:
				rating_movist = 0
			
			#pattern = re.compile('[^A-Za-z0-9]+')
			#title_eng = pattern.sub('',movie.title_eng)
			
			# IMDB 정보 
			if title_eng:
				try:
					imdb_api = self.imdb.get_imdb_data(title_eng)
					rating_imdb = imdb_api.get('Rating')
					
					try:
						print u'imdb평점 수집완료: ' , rating_imdb
					except:
						pass
				except Exception as e:
					rating_imdb = 0
			
			if rating_imdb == 'N/A':
				rating_imdb = 0
				
			movie.rating_daum = rating_daum
			movie.rating_naver = rating_naver
			movie.rating_imdb = rating_imdb
			movie.rating_movist = rating_movist
			movie.save()
		
		try:
			print u'스크립트수행시간 :  %.02f' % (time.time() - t)
		except:
			pass
