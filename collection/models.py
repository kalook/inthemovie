from django.db import models

__author__ = 'lunyx'

class Movies(models.Model):
    title_kor = models.CharField(max_length=255)
    def __init__(self):
        pass
