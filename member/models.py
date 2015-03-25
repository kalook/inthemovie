#from django.contrib import admin
#from member.models import *
from django.db import models
# Create your models here.

class Users(models.Model):
    user_id     = models.CharField(max_length=20, unique=True)
    password    = models.CharField(max_length=100)
    name        = models.CharField(max_length=20)
    email       = models.CharField(max_length=100)
    nick_name   = models.CharField(max_length=20)
    mobile_phone= models.CharField(max_length=30)
    point       = models.IntegerField(default=500)
    ip          = models.CharField(max_length=15)
    is_open     = models.CharField(max_length=1)
    is_auth     = models.CharField(max_length=1)
    is_admin    = models.CharField(max_length=1,default='N')
    edit_date   = models.DateTimeField(auto_now_add=True)
    reg_date    = models.DateTimeField(auto_now_add=True)
    
class Points(models.Model):
    user        = models.ForeignKey(Users)
    type        = models.CharField(max_length=3)
    point       = models.IntegerField(default=0)
    description = models.CharField(max_length=255)
    ip          = models.CharField(max_length=15)
    reg_date    = models.DateTimeField(auto_now_add=True)
    
class Messages(models.Model):
    is_notice   = models.CharField(max_length=1)
    sender_id   = models.CharField(max_length=20)
    recipient_id= models.CharField(max_length=20)
    send_date   = models.DateTimeField(auto_now_add=False)
    read_date   = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    content     = models.TextField()
    ip          = models.CharField(max_length=15)
    reg_date    = models.DateTimeField(auto_now_add=True)

class Dropouts(models.Model):
	user_id  = models.CharField(max_length=20, unique=True)
	name     = models.CharField(max_length=20)
	reg_date = models.DateTimeField(auto_now_add=True)
	
class Sns(models.Model):
	user = models.ForeignKey(Users)
	service = models.CharField(max_length=20)
	oauth_token = models.CharField(max_length=255)
	create_date = models.DateTimeField(auto_now_add=True)
	