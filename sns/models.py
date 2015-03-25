from django.db import models
from member.models import *
from event.models import Events
from movies.models import *

class SocialComment(models.Model):
	uesr = models.ForeignKey(Users, null=True)
	event = models.ForeignKey(Events, null=True)
	movie = models.ForeignKey(Movies, null=True)
	email = models.CharField(max_length=255)
	username = models.CharField(max_length=30)
	link = models.CharField(max_length=1024)
	service = models.CharField(max_length=20)
	content =  models.CharField(max_length=1024)
	profile_image = models.CharField(max_length=1024, null=True)
	create_date = models.DateTimeField(auto_now_add=True)