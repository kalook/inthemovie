# -*- coding: utf-8 -*-

from django.db import models
from django.db import IntegrityError
from datetime import datetime
from member.models import *
import datetime
# Create your models here.
class Emails(models.Model):
	user		= models.ForeignKey(Users)
	title		= models.CharField(max_length=255)
	content		= models.TextField()
	ip			= models.CharField(max_length=15)
	is_send		= models.CharField(max_length=1)
	reg_date	= models.DateTimeField(auto_now_add=True)
	
class Ads(models.Model):
	user			= models.ForeignKey(Users)
	url				= models.CharField(max_length=1024)
	banner_image	= models.CharField(max_length=255)
	type			= models.CharField(max_length=30)
	new_window		= models.CharField(max_length=1)
	show_service	= models.CharField(max_length=30)
	start_date		= models.DateField()
	end_date		= models.DateField()
	reg_date		= models.DateTimeField(auto_now_add=True)

# 배너관리
class Banner(models.Model):
    banner_root = models.CharField(max_length=255,null=True)
    link = models.URLField(max_length=255)
    position = models.CharField(max_length=50)
    blank = models.CharField(max_length=50)
    start_date = models.DateField()
    last_date = models.DateField()
    

	