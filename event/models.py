from django.db import models
from member.models import *
from movies.models import *

# Create your models here.
class Events(models.Model):
	user	= models.ForeignKey(Users)
	type	= models.CharField(max_length=20)
	req_type = models.CharField(max_length=20,default='normal',null=True)
	movie = models.ForeignKey(Movies, null=True)
	movie_title	= models.CharField(max_length=255)
	subject = models.CharField(max_length=255)
	thumnail_image = models.CharField(max_length=200)
	main_image  = models.CharField(max_length=200,null=True)
	vod_url  = models.CharField(max_length=1024, null=True)
	date = models.CharField(max_length=100)
	place = models.CharField(max_length=100)
	people = models.CharField(max_length=100)
	people_count = models.IntegerField(default=0)
	announce = models.CharField(max_length=100)
	main_content = models.TextField()
	rule_content = models.TextField()
	status = models.CharField(max_length=20)
	ip_addr	= models.CharField(max_length=15)
	comment_type = models.CharField(max_length=1, null=True, default='F')
	create_date = models.DateTimeField(auto_now_add=True)
	edit_date = models.DateTimeField(auto_now_add=False, null=True)
	
class Request(models.Model):
	event = models.ForeignKey(Events)
	user = models.ForeignKey(Users)
	type = models.CharField(max_length=20)
	req_type = models.CharField(max_length=20)
	req_location = models.CharField(max_length=20, null=True, default='web')
	use_point = models.IntegerField(default=0)
	comment = models.CharField(max_length=500)
	ip_addr	= models.CharField(max_length=15)
	req_date = models.DateTimeField(auto_now_add=True)

class Panalty(models.Model):
	user = models.ForeignKey(Users)
	reason = models.CharField(max_length=500)
	start_date = models.DateField(auto_now_add=False) 
	end_date = models.DateField(auto_now_add=False) 
	ip_addr	= models.CharField(max_length=15)
	create_date = models.DateTimeField(auto_now_add=True) 

