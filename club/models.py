from django.db import models
from member.models import *
from movies.models import *

class Boards(models.Model):
    code        = models.CharField(max_length=20)
    title       = models.CharField(max_length=255)
    type        = models.CharField(max_length=20)
    reg_date    = models.DateTimeField(auto_now_add=True)
    

class Posts(models.Model):
    board       = models.ForeignKey(Boards)
    user        = models.ForeignKey(Users)
    title       = models.CharField(max_length=255)
    content     = models.TextField()
    thumnail	= models.CharField(max_length=255, blank=True, null=True)
    readed_count= models.IntegerField(default=0)
    ip          = models.CharField(max_length=15)
    reg_date    = models.DateTimeField(auto_now_add=True)
    edit_date   = models.DateTimeField(auto_now_add=True)
    movie	    = models.ForeignKey(Movies ,blank=True, null=True)
    geo_coding  = models.CharField(max_length=255 ,blank=True, null=True)
    url         = models.URLField(max_length=255 ,blank=True, null=True)

class Comments(models.Model):
    board       = models.ForeignKey(Boards)
    post        = models.ForeignKey(Posts)
    user        = models.ForeignKey(Users)
    comment     = models.TextField()
    ip          = models.CharField(max_length=15)
    reg_date    = models.DateTimeField(auto_now_add=True)
    edit_date   = models.DateTimeField(auto_now_add=True)
    
class Files(models.Model):
    board           = models.ForeignKey(Boards)
    post            = models.ForeignKey(Posts)
    user            = models.ForeignKey(Users)
    file_name       = models.CharField(max_length=255)
    type            = models.CharField(max_length=1)
    ip              = models.CharField(max_length=15)
    reg_date        = models.DateTimeField(auto_now_add=True)
    edit_date       = models.DateTimeField(auto_now_add=True)
    
class Tags(models.Model):
    post        = models.ManyToManyField(Posts)
    user        = models.IntegerField(default=0)
    tag         = models.CharField(max_length=100)
    reg_date    = models.DateTimeField(auto_now_add=True)
    
