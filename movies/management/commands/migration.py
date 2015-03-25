# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
from xml.dom import minidom
from libs.flicker import *
from member.models import *
from admin.models import *
from club.models import *
import time
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
import MySQLdb
import time
class Command(BaseCommand):
	# 언어환경
	LANG = "utf-8"

	args = '<poll_id poll_id ...>'
	help = 'Closes the specified poll for voting'
	
	def handle(self, *args, **options):	
		t = time.time()
		db = MySQLdb.connect(db='dducks', user='kinkim', passwd='kyhs1167', host='sysopclub.com', charset='utf8',use_unicode=True)
		self.migration_user(db)
		self.migration_message(db)
		self.migration_board(db)
		print '스크립트수행시간 :  %.02f' % (time.time() - t)
		
		
	def migration_user(self, db):
		cursor = db.cursor()
		query = "SELECT mb_id, mb_password, mb_name, mb_nick, mb_email, mb_hp, mb_datetime,mb_ip,mb_point FROM g4_member WHERE mb_password<>'' AND mb_email<>'' AND mb_name<>'' AND mb_nick<>''"
		cursor.execute(query)
		member_list = cursor.fetchall()
		for member in member_list:
			user = Users.objects.create(
					user_id				 = member[0],
					password				= member[1],
					name			= member[2],
					nick_name		   = member[3],
					mobile_phone		= member[5],
					email				   = member[4],
					ip			  = member[7],
					is_auth				 = 'y',
					reg_date 	  = member[6],
					point	  = member[8]
			)	
			print '------------'+user.user_id+'----'+user.name+'------------'
			print '-------포인트 로그---------'	
			sql = "SELECT mb_id, po_datetime, po_content, po_point FROM g4_point WHERE mb_id = \'"+member[0]+"\'"
			print sql
			cursors = db.cursor()
			cursors.execute(sql)
			point_list = cursors.fetchall()
			for points in point_list:
				point_type = ''
				if points[3]>0:
					point_type = 'get'
				else:
					point_type = 'use'
				point = Points.objects.create(
						user = user,
						type = point_type,
						point = points[3],
						description = points[2],
						ip = '127.0.0.1',
						reg_date = points[1]
				)
				print point.user.user_id

	def migration_message(self, db):
		cursor = db.cursor()
		query = "SELECT me_recv_mb_id, me_send_mb_id, me_send_datetime, me_read_datetime, me_memo FROM g4_memo"
		cursor.execute(query)
		msg_list = cursor.fetchall()
		for msg in msg_list:
			message = Messages.objects.create(
				is_notice = 'n',
				sender_id = msg[0],
				recipient_id = msg[1],
				send_date = msg[2],
				read_date = msg[3],
				content = msg[4],
				ip = '127.0.0.1'
			)
			print message.sender_id+'----'+message.recipient_id
	
	def setData(self, db, data_list, board, boards):
		for post in data_list:
			print post
			try:
				user_info = Users.objects.get(user_id=post[7])
				article = Posts.objects.create(
					board = board,
					user = user_info,
					title = post[4],
					content = post[5],
					readed_count = post[6],
					ip = post[8],
					reg_date = post[9]
				)
				comment_cursor = db.cursor()
				qry = "SELECT wr_id,  wr_parent,  wr_is_comment, ca_name, wr_subject, wr_content, wr_hit, mb_id, wr_ip, wr_datetime FROM  g4_write_"+boards+" WHERE wr_is_comment = 1 AND wr_parent ="+str(post[0])
				comment_cursor.execute(qry)
				comment_list = comment_cursor.fetchall()
				for comment in comment_list:
					print comment
					try:
						user_infos = Users.objects.get(user_id=comment[7])
						comm_ent = Comments.objects.create(
							board = board,
							post = article,
							user = user_infos,
							comment = comment[5],
							ip = comment[8],
							reg_date = post[9]
						)
					except Exception as e:
						pass						
			except Exception as f:
				pass


	
	def migration_board(self, db):
		
		board_list = ['info_sesang','comm_ticket', 'event_notice', 'comm_repo', 'comm_mania', 'info_myungso', 'comm_koong', 'meet_jung',]
		for boards in board_list:
			if boards == 'comm_mania':
				#영화먼저
				qrys1 = "SELECT wr_id,  wr_parent,  wr_is_comment, ca_name, wr_subject, wr_content, wr_hit, mb_id, wr_ip, wr_datetime FROM  g4_write_"+boards+" WHERE wr_is_comment = 0 AND ca_name IN ('영화강추', '영화비범', '영화평범', '영화비추')"
				movie_board = board = Boards.objects.get(code='movie')
				movie_cursor = db.cursor()
				movie_cursor.execute(qrys1)
				movie_list = movie_cursor.fetchall()
				self.setData(db, movie_list, movie_board, boards)
				
				#공연먼지
				qrys2 = "SELECT wr_id,  wr_parent,  wr_is_comment, ca_name, wr_subject, wr_content, wr_hit, mb_id, wr_ip,wr_datetime FROM  g4_write_"+boards+" WHERE wr_is_comment = 0 AND ca_name IN ('공연강추', '공연비범', '공연평범', '공연비추')"
				performance_board = board = Boards.objects.get(code='performance')
				performance_cursor = db.cursor()
				performance_cursor.execute(qrys2)
				performance_list = performance_cursor.fetchall()
				self.setData(db, performance_list, performance_board, boards)				
				
				
			else:
				sql = "SELECT wr_id,  wr_parent,  wr_is_comment, ca_name, wr_subject, wr_content, wr_hit, mb_id, wr_ip,wr_datetime FROM  g4_write_"+boards+" WHERE wr_is_comment = 0"
				print sql
				# 게시판 정보
				if boards == 'comm_ticket':
					board = Boards.objects.get(code='ticket')
				elif boards == 'event_notice':
					board = Boards.objects.get(code='announce')
				elif boards == 'comm_repo':
					board = Boards.objects.get(code='reporter')
				elif boards == 'info_sesang':
					board = Boards.objects.get(code='reporter')
				elif boards == 'info_myungso':
					board = Boards.objects.get(code='attraction')
				elif boards == 'comm_koong':
					board = Boards.objects.get(code='free')
				elif boards == 'meet_jung':
					board = Boards.objects.get(code='offmeeting')

				cursor = db.cursor()
				cursor.execute(sql)
				post_list = cursor.fetchall()	
				self.setData(db, post_list, board, boards)
	
					
				
		
		

