#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: SunGyo Kim
# Email: Kimsg1984@gmail.com
# irc.freenode #ubuntu-ko Sungyo
'''
[입출력 모듈]

- 상위 클래스 : OS.py # 오퍼레이팅 시스템 모듈

*-- 메모사항 --* 
- 로그 사용 방법: 
	Log	= IO.Log(path='/path/you/want', log_name='mylogger', log_file='IO.log')   #Log.Logger.error('txt')

pymodule_path='/home/sungyo/Unison/script/module/python'
import sys

#커스텀 모듈
sys.path.append(pymodule_path)
import IO

'''

# <import> ----------------------------------------------------------------------
import csv
import datetime
import inspect # 함수명 호출시
import logging
import logging.handlers
import os
import re
import shelve
import subprocess
import pynotify
import sys
reload(sys)
sys.setdefaultencoding('utf-8') # 한글 입출력을 위한 설정
# <import/> ---------------------------------------------------------------------

# environnement vars : 노티 설정
id = subprocess.check_output('whoami').strip()
os.environ.setdefault('XAUTHORITY', '/home/%s/.Xauthority' %id)
os.environ.setdefault('DISPLAY', ':0.0')

dir_corrent = os.getcwd()

class File:
	def read(self, *args):
		t 		= args[0]
		contentFile = open(r'%s' %t)
		content 	= contentFile.read()
		contentFile.close()
		return content
	
	def save(self, *args): # content, file
		content 		= args[0]
		f 			= args[1]
		
		if f[0] is '.' or '/':
			save_file 	= open('%s' %f, 'w') # a: 쓰기 + 이어쓰기 모드
		else:	
			save_file 	= open('./%s' %f, 'w') # a: 쓰기 + 이어쓰기 모드

		save_file.write('%s' %content)
		save_file.close()
		if os.path.exists(f): 
			return True
		else: 
			Log.Logger.error('파일 쓰기에 실패하였습니다: %s' %f)
			return False			

	def add(self, *args): # content, file
		content 		= args[0]
		f 			= args[1]
		
		if f[0] is '.' or '/':
			save_file 	= open('%s' %f, 'a') # a: 쓰기 + 이어쓰기 모드
		else:	
			save_file 	= open('./%s' %f, 'a') # a: 쓰기 + 이어쓰기 모드

		save_file.write('%s' %content)
		save_file.close()
		
class Log():
	'''
	- 사용법: Log.Logger.debug('기록할 로그 내용을 적습니다')
	- debug, info, warning, error, critical 등의 로그 기록이 가능합니다. 
	- 로그 클래스를 각 파일 내에서 선언해 주어야 '파일 이름'과 '함수명'이 함께 기재됩니다.

	+------------------+
	|  CRITICAL	50	|
	|  ERROR		40	|
	|  WARNING	30	|
	|  INFO		20	|
	|  DEBUG		10 	|
	|  NOTSET	0 	|
	+------------------+

	파이썬 로거 사용법 http://www.hanbit.co.kr/network/view.html?bi_id=1979
	'''
	def __init__(self, path=dir_corrent, log_name='mylogger', log_file='IO.log', filelogging=True):
		# pass
		self.Logger = logging.getLogger(log_name) # 로거 인스턴스를 만든다
		file_max_byte = 1024 * 1024 * 1 #1MB
		filename = os.path.join(path, log_file)
		fomatter = logging.Formatter('%(asctime)s [%(filename)s:%(lineno)s|%(levelname)s]\t %(message)s') # 포매터를 만든다

		# 스트림 핸들러
		streamHandler = logging.StreamHandler()
		streamHandler.setFormatter(fomatter)
		self.Logger.addHandler(streamHandler)

		# 파일 핸들러
		if filelogging:
			fileHandler = logging.handlers.RotatingFileHandler(filename, maxBytes=file_max_byte, backupCount=3) # 1메가짜리 파일 3개
			fileHandler = logging.FileHandler(filename)
			fileHandler.setFormatter(fomatter)
			self.Logger.addHandler(fileHandler) 

		# 로거 인스턴스로 로그를 찍는다.
		self.Logger.setLevel(logging.DEBUG)

class Csv:
	def __init__(self, filename='Test.csv'):
		self.Log=Log()

		filename = filename
		try:
			csv_file = open(filename, 'rb')
			reader = csv.reader(csv_file)
			for row in reader:
	    			print(row)
		except:
			csv_file = open(filename, "w")
			cw = csv.writer(csv_file , delimiter=',', quotechar='|')
			# cw.writerow(["name", "age", "address", "phone"])
			csv_file.close

# # U.I

class Shelve(): # db 저장하고 읽어오기
	""" 
	https://docs.python.org/2/library/shelve.html (기본적인 설명) 
	http://gwlee.blogspot.kr/2012/03/shelve.html (대용량으로 다룰 경우)
	""" 
	def __init__(self, filename='IO_db.dat'):
		self.db_file = filename

	def save(self, obj, sub, id=None):
		self.db = shelve.open(self.db_file)

		if id : 
			if self.db.has_key(id): 
				list = self.db[id]
				list[obj] = sub
				self.db[id] = list
				self.db.close()
				return True
			else: 
				list = {}
				list[obj] = sub
				self.db[id] = list
				self.db.close()
				return True
		else: 
			self.db[obj]	=sub 
			self.db.close()
			return False

	def load(self, obj, id=False):
		self.db = shelve.open(self.db_file)
		if id:
			if self.db.has_key(id):
				if self.db[id].has_key(obj): 
					result = self.db[id][obj]
					self.db.close()
					return result
		else:
			if self.db.has_key(obj): 
				result = self.db[obj]
				self.db.close()
				return result
		self.db.close()
		return 'Null'

	def hasKey(self, obj, id=None):
		self.db = shelve.open(self.db_file)
		if id:
			if self.db.has_key(id): 
				if self.db.has_key(obj): 
					self.db.close()
					return True 
		else: 
			if self.db.has_key(obj): 
				self.db.close()
				return True
		self.db.close()
		return False 

	def list(self):
		db_result = {}
		self.db = shelve.open(self.db_file)
		for d in self.db: db_result[d] = self.db[d]
		self.db.close()
		return db_result

	def removeAll(self):
		self.db = shelve.open(self.db_file)
		for f in self.db: 
			del self.db[f]
		self.db.close()
		return True

	def remove(self, obj): 
		self.db = shelve.open(self.db_file)
		if self.db.has_key(obj): 
			del self.db[obj] 
			if self.db.has_key(obj) == False: # has removed
				self.db.close()
				return True
			else:
				self.db.close()
				return False
		else:	
			self.db.close()
			return True

# # U.I

def mail(*args): # mail_to_send, title, content

	try:
		mail_to_send 	= args[0]
		title			= args[1]
		content		= args[2]
	except:
		Log.Logger.error('인자값이 제대로 넘어오지 않았습니다...mail_to_send, title, content')
		return 0
	F = File()

	SENDMAIL = "/usr/sbin/sendmail" # sendmail location
	p = os.popen("%s -t" % SENDMAIL, "w")
	p.write("To: %s\n" %mail_to_send)
	p.write("Subject: %s\n" %title)
	p.write("\n") # blank line separating headers from body
	p.write("%s\n" %content)
	sts = p.close()
	if sts != 0:
		print("Sendmail exit status" + str(sts) )

	'''	
	F.save(content,'IO_mail2send.txt')
	
	subprocess.call(['echo', 'test', '|' ,'mutt', '-x', '-s', title , mail_to_send])
	# mutt -x -a 파일_이름 -s "메일제목" "메일주소"
	# os.remove('IO_mail2send.txt')
	'''

def noti(message, title = 'pynoti'):
    pynotify.init("Test")
    notice = pynotify.Notification(title, message)
    notice.show()
    return

def pnt(content):
	print(content)