from django.db import models
from member.models import *

class Movies(models.Model):
	title_kor		= models.CharField(max_length=255)
	title_eng   	= models.CharField(max_length=255, null=True)
	title_url		= models.CharField(max_length=255, null=True)
	type			= models.CharField(max_length=20)
	is_keyword		= models.CharField(max_length=1, default='F')
	show			= models.CharField(max_length=1)
	rating_naver	= models.FloatField(null=True)
	rating_daum		= models.FloatField(null=True)
	rating_imdb		= models.FloatField(null=True)
	rating_movist	= models.FloatField(null=True)
	thumnail		= models.CharField(max_length=1024, null=True)
	display_date	= models.DateTimeField(auto_now_add=False, null=True)
	create_date		= models.DateTimeField(auto_now_add=True)
	count_photo		= models.IntegerField(null=True)
	count_vod		= models.IntegerField(null=True)
	count_bbs		= models.IntegerField(null=True)
	count_press		= models.IntegerField(null=True)
	count_twitter	= models.IntegerField(null=True)
	count_me2day	= models.IntegerField(null=True)
	count_blog		= models.IntegerField(null=True)
	link_daum		= models.CharField(max_length=1024,null=True)
	link_naver		= models.CharField(max_length=1024,null=True)
	link_imdb		= models.CharField(max_length=1024,null=True)
	link_tomato		= models.CharField(max_length=1024,null=True)
	link_movist		= models.CharField(max_length=1024,null=True)
	is_collected	= models.CharField(max_length=1, null=True)
	#show_date		= models.CharField(max_length=120,null=True)


	def get_avg_rating(self):
		#ratingNaver, ratingDaum, ratingImdb = 0
		if self.rating_naver == None:
			self.rating_naver = 0
		if self.rating_daum == None:
			self.rating_daum = 0
		if self.rating_imdb == None:
			self.rating_imdb = 0
		if self.rating_movist == None:
			self.rating_movist = 0
		ls = []
		ls.append(self.rating_naver)
		ls.append(self.rating_daum)
		ls.append(self.rating_imdb)
		ls.append(self.rating_movist)

		
		counting = 0
		sum = 0
		for count in ls:
			if not count==0:
				sum+=float(count)
				counting+=1
		try:
			return round(sum/counting,1)
		except Exception as e:
			return 0
		'''

		if int(self.rating_daum) == 0:
			if not self.rating_naver:
				return self.rating_imdb
			elif not self.rating_imdb:
				return self.rating_naver
			else:
				return round((self.rating_naver+self.rating_imdb)/2, 1)
		
		elif int(self.rating_naver) == 0:
			if not self.rating_daum:
				return self.rating_imdb
			elif not self.rating_imdb:
				return self.rating_daum
			else:
				return round((self.rating_daum+self.rating_imdb)/2, 1)
		
		elif int(self.rating_imdb) == 0:
			if not self.rating_naver:
				return self.rating_daum
			elif not self.rating_daum:
				return self.rating_naver
			else:
				return round((self.rating_naver+self.rating_daum)/2, 1)
		
		elif int(self.rating_movist) == 0:
			if not self.rating_naver:
				return self.rating_daum
			elif not self.rating_daum:
				return self.rating_naver
			else:
				return round((self.rating_naver+self.rating_daum)/2, 1)
		else:
			try:
				return round((self.rating_naver+self.rating_daum+self.rating_imdb+self.rating_movist)/4, 1)
			except Exception as e:
				return 0
		'''

	def get_all_counts(self):
		total = 0
		if self.count_bbs:
			total = total + self.count_bbs
	
		if self.count_press:
			total = total + self.count_press

		if self.count_twitter:
			total = total + self.count_twitter

		if self.count_me2day:
			total = total + self.count_me2day

		if self.count_blog:
			total = total + self.count_blog	
			
		return total
		
class CollectData(models.Model):
	movie		= models.ForeignKey(Movies)
	type		= models.CharField(max_length=20)
	link_url	= models.CharField(max_length=1024)
	subject		= models.CharField(max_length=255)
	content_url = models.CharField(max_length=1024)
	swf_url		= models.CharField(max_length=1024)
	edit_date	= models.DateTimeField(auto_now_add=False, null=True)
	create_date	= models.DateTimeField(auto_now_add=True)
	content_date = models.DateTimeField(null=True)
	
class Wordreplace(models.Model):
	kor_letter = models.CharField(max_length=30, null=True)
	eng_letter = models.CharField(max_length=30, null=True)