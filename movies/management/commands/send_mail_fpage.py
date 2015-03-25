# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
import simplejson
from xml.dom import minidom
from libs.api_request import *
from member.models import *
from admin.models import *
import time
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
import glob
import logging
import logging.handlers

class Command(BaseCommand):
	# 언어환경
	LANG = "utf-8"

	args = '<poll_id poll_id ...>'
	help = 'Closes the specified poll for voting'
	
	def handle(self, *args, **options):	
		LOG_FILENAME = '/home/inthemovie/logs/mail_send.log'
		my_logger = logging.getLogger('mail send')
		my_logger.setLevel(logging.DEBUG)
		handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=2000, backupCount=10)
						
		title = "fpage test"
		content = "test email"
		mail = "pcmwooki@naver.com"
		try:
			msg = EmailMultiAlternatives(title, content, 'contact@fpage.kr', [mail])
			msg.attach_alternative(content, "text/html")
			msg.send()
		except Exception as e:
			print "not send mail"
			print e