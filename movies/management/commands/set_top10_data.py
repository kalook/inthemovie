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
		#수집 초기화
		#now_show = Movies.objects.filter(type='naver_keyword',is_collected = 'T', show = 'N')
		#for now in now_show:
		#	now.is_collected = 'F'
		#	now.save()		
		now_show1 = Movies.objects.filter(type='naver_keyword',is_collected = 'T',is_keyword='T', show = 'N')
		for now in now_show1:
			now.is_collected = 'F'
			now.is_keyword = 'F'
			now.save()
		now_show2 = Movies.objects.filter(type__in=['naver_premovie','naver_current'],is_collected = 'T', is_keyword='T', show = 'N')
		for now in now_show2:
			now.is_collected = 'F'
			now.is_keyword = 'F'
			now.save()
		
		keywords = self.naver.get_search_keyword('ranktheme','movie')
			
		self._config_movie_name(keywords,'naver_keyword')

		movie_list = Movies.objects.filter(is_collected = 'T',is_keyword='T')

		for movie in movie_list:
			title_eng = link_daum = link_naver = thumnail = link_imdb = link_movist =''
			rating_naver = rating_daum = rating_imdb = rating_movist = 0	
			count_photo =count_vod =count_bbs =count_press = count_press = 0
			count_twitter = count_me2day = count_blog = 0			
			
			title = movie.title_kor
			title_api = '영화' + movie.title_kor.encode('utf-8')

			try:
				print title
			except:
				pass

				
			#네이버 영화 기본정보
			naver_api,movie_count = self.naver.getAPI('movie',title.encode("utf-8"))
			if naver_api:
				title_eng = naver_api[0].get('subtitle')
				rating_naver = naver_api[0].get('userRating')
				link_naver = naver_api[0].get('link')
				thumnail = naver_api[0].get('image')
			
			title_url = self._get_title_url(title_eng, title)
			paths = "/data/inthemovie/files/hotmovie/"
			thumnail = thumnail.replace('mit110','mi')
			if thumnail:
				img_data = urllib.urlopen(thumnail) 
				img_io = StringIO(img_data.read()) 
				im = Image.open(img_io) 
				im.thumbnail((210, 268), Image.ANTIALIAS) 
				im.save(paths+datetime.now().strftime('%Y-%m-%d')+"_"+title_url+".jpg")			
				thumnail = "/files/hotmovie/"+datetime.now().strftime('%Y-%m-%d')+"_"+title_url+".jpg"

			#다음 영화 기본정보
			daum_movie_api = self.daum.getAPI({"type":"contents","service":"movie","q":title.encode("utf-8")})
			if daum_movie_api:
				item = daum_movie_api['channel']	
				contents = item['item']
				for content in contents:
					for row in content['title']:
						
						if movie.link_daum:
							rating_daum = self.daum.getDaumRating(movie.link_daum)
						else:
							link_daum = row.get('link')
							rating_daum = self.daum.getDaumRating(row.get('link'))
						
			#다음 동영상 검색
			vod_api = self.daum.getAPI({"type":"search","service":"vclip","q":title_api})
			if vod_api:
				#print vod_api
				item = vod_api['channel']
				count_vod =  item['totalCount']
				try:
					print "다음 동영상 : " + count_vod
				except:
					pass
				
				contents = item['item']
				for content in contents:
					subject = content.get('title')
					try:
						collect_data = CollectData.objects.get(subject=subject)
					except CollectData.DoesNotExist:
						data = CollectData.objects.create(
							movie = movie,type = 'vod', link_url = content.get('link'),
							subject = subject, swf_url	= content.get('player_url'),
							content_url = content.get('thumbnail'))
						data.save()
			
			#이미지 검색
			image_api,count_photo = self.naver.getAPI('image',title_api)
			if image_api:
				try:
					print u"네이버 이미지 : "+count_photo
				except:
					pass

				for img in image_api:
					try:
						collect_data = CollectData.objects.get(subject=(image_api[img]).get('title'))
					except CollectData.DoesNotExist:
						thumnail_url = (image_api[img]).get('thumbnail')
						content_url = thumnail_url.split('=', 1)
						data = CollectData.objects.create(
							movie = movie, type = 'image', link_url = (image_api[img]).get('link'),
							subject = (image_api[img]).get('title'), content_url = content_url[1])
						data.save()

			#네이버 블로그
			blog_api, blog_count = self.naver.getAPI('blog',title_api)
			if blog_api:
				try:
					print u"네이버 블로그 : "+blog_count
				except:
					pass
				for blog in blog_api:	
					try:
						collect_data = CollectData.objects.get(subject=(blog_api[blog]).get('title'))
					except CollectData.DoesNotExist:
						data = CollectData.objects.create(
							movie = movie,type = 'naver_blog',link_url = (blog_api[blog]).get('link'),
							subject = (blog_api[blog]).get('title'),content_url = '')
						data.save()

			#네이버 뉴스
			news_api, news_count = self.naver.getAPI('news',title_api)
			if news_api:
				try:
					print u"네이버 뉴스 : "+news_count
				except:
					pass
				for news in news_api:
					try:
						collect_data = CollectData.objects.get(subject=(news_api[news]).get('title'))
					except CollectData.DoesNotExist:
						data = CollectData.objects.create(
							movie = movie,type = 'naver_news',link_url = (news_api[news]).get('link'),
							subject = (news_api[news]).get('title'),content_url = '')
						data.save()
			
			
			#다음 뷰
			view_api = self.daum.getViewAPI(title.encode("utf-8"))
			daum_view_count = view_api.getElementsByTagName("total_count")
			try:
				count_blog = daum_view_count[0].firstChild.data
				try:
					print u"다음뷰 카운트 :"+count_blog
				except:
					pass
				
			except Exception as e:
				pass
			news_list = view_api.getElementsByTagName("news")
			if news_list:
				link = image_url = view_title = ''
				for news in news_list:
					view_title = news.getElementsByTagName("title")[0].firstChild.data
					try:
						image_url = news.getElementsByTagName("image_url")[0].firstChild.data
					except:
						image_url = ''
						link = news.getElementsByTagName("url")[0].firstChild.data

						try:
							collect_data = CollectData.objects.get(subject=title)
						except CollectData.DoesNotExist:
							data = CollectData.objects.create(
								movie = movie, type = 'daum_view', link_url = link,
								subject = view_title, content_url = image_url,
								content_date = news.getElementsByTagName("reg_date")[0].firstChild.data)
							data.save()

			# IMDB 정보 
			if title_eng:
				imdb_api = self.imdb.get_imdb_data(title_eng)
				try:
					rating_imdb = imdb_api.get('Rating')
					link_imdb = "http://www.imdb.com/title/"+imdb_api.get('ID')+"/"
					try:
						print u'imdb API : ', imdb_api
						print u'imdb Rating : ', rating_imdb
						print u'imdb Link : ', link_imdb
					except:
						pass
					
				except Exception as e:
					rating_imdb = 0

			if rating_imdb == 'N/A':
				rating_imdb = 0
			
			# movist 정보 
			
			
			try:
				movist_api = self.movist.get_movist_data(title)
				if movist_api.get('state') =='N':
					rating_movist =0
					link_movist = ''
				else:
					rating_movist = movist_api.get('average')
					link_movist = movist_api.get('link')
					try:
						print u'무비스트 API : ', movist_api
						print u'무비스트 Rating : ', rating_movist
						print u'무비스트 URL : ', link_movist
					except:
						pass

			except Exception as e:
				rating_movist = 0
				link_movist =''
			


			#title_info = Movies.objects.get(title_kor=title)
			movie.title_eng = title_eng
			movie.rating_naver = rating_naver
			movie.rating_daum = rating_daum
			movie.rating_imdb = rating_imdb
			movie.rating_movist = rating_movist
			
			movie.link_imdb = link_imdb
			movie.link_movist = link_movist
			movie.link_naver = link_naver
			if not link_daum =='':
				movie.link_daum = link_daum
			movie.thumnail = thumnail
			movie.title_url = title_url
			movie.display_date = datetime.now().strftime('%Y-%m-%d')
			movie.count_photo	= count_photo
			movie.count_vod	= count_vod
			movie.count_bbs	= 0
			movie.count_press	= 0
			movie.count_twitter= 0
			movie.count_me2day	= 0
			movie.count_blog = count_blog
			movie.save()								

		try:
			print u'스크립트수행시간 :  %.02f' % (time.time() - t)		
		except:
			pass



	def _config_movie_name(self, movies, types):
		for movie in movies:
			title = movie.replace(' ','')
			title = title.encode('utf-8').replace('영화','')
			try:
				print title.encode("utf-8")
			except:
				pass
			
			try:
				movie_title = Movies.objects.filter(title_kor=title)
				for list in movie_title:
					list.is_collected = 'T'
					list.is_keyword = 'T'
					list.type = types
					list.save()
					try:
						print list.title_kor.encode("utf-8") + ' ==> collected'
					except:
						pass
				if not movie_title:
					movie = Movies.objects.create(
						title_kor = title,
						type = types,
						show = 'N',
						is_collected = 'T',
						is_keyword = 'T',
						link_daum = ''
					)
					movie.save()
					
			except Movies.DoesNotExist:
				try:
					print title , ' ==> new'
				except:
					pass

				movie = Movies.objects.create(
						title_kor = title,
						type = types,
						show = 'N',
						is_collected = 'T',
						is_keyword = 'T',
						link_daum = ''
				)
				movie.save()
				
	def _get_title_url(self, title_eng, title_kor):
		title_url = ''
		pattern = re.compile('[^A-Za-z0-9]+')
		title_eng = pattern.sub('',title_eng)
		print title_eng
		if title_eng:
			title_url = title_eng.replace('-','')
			title_url = title_url.replace(',','')
			title_url = title_url.replace(':','')
			title_url = title_url.replace('.','')
			title_url = title_url.replace("'",'')
			title_url = title_url.replace("`",'')
			title_url = title_url.replace(' ','')
			title_url = title_eng
		else:
			kor_letter_title = ''
			for kor_letter in title_kor:
				try:
					eng_lett = Wordreplace.objects.get(kor_letter=kor_letter)
					kor_letter_title = kor_letter_title + eng_lett.eng_letter
				except Wordreplace.DoesNotExist:
					pass
				title_url = kor_letter_title
		
		title_url_list = Movies.objects.filter(title_url=title_url)
		tlt_count = len(title_url_list)
		if tlt_count>1:
			title_url = title_url + '1'

		return title_url
