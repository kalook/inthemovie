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
						
		email_info = Emails.objects.filter(is_send = 'P')
		if email_info:
			user_info = Users.objects.all()
			for email in email_info:
				mail_count = 0
				for user in user_info:
					try:
						print user.user_id
						msg = EmailMultiAlternatives(email.title, email.content, 'contact@inthe-movie.com', [user.email])
						msg.attach_alternative(email.content, "text/html")
						msg.send()
					except Exception as e:
						pass
						#my_logger.debug('%s ERROR 메일이 전송되지 못했습니다. ' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
						#my_logger.debug(user.email)
					mail_count + mail_count + 1
				email.is_send = 'S'
				email.save()
				if mail_count%100 == 0:
					time.sleep(1.5)
				#my_logger.debug('%s %s count = %d' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), email.title.encode('utf-8'), mail_count))
		else:
			pass
			#my_logger.debug('%s ------보낼 메일이 없습니다.------' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

