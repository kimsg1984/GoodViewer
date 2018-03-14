#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: SunGyo Kim
# Email: Kimsg1984@gmail.com
# irc.freenode #ubuntu-ko Sungyo

'''
[오퍼레이팅 시스템]
- 디렉토리와 파일을 관리하는 FileManager의 역할을 합니다.
- 기본적인 명령어들을 구현하는데 집중합니다.


os.path 		-> http://devanix.tistory.com/298
ls *.txt 	-> http://stackoverflow.com/questions/5629242/getting-every-file-in-a-directory-python

'''

DIR_PYMODULE = '/home/sungyo/Unison/script/module/python'

# <import> ----------------------------------------------------------------------
import os
import sys
import shutil
import subprocess
reload(sys)
sys.setdefaultencoding('utf-8') 	# 한글 입출력을 위한 설정
sys.path.append(DIR_PYMODULE)	# 커스텀 모듈
import IO

# <import/> ----------------------------------------------------------------------

Log1	= IO.Log()   #Log1.Logger.error('txt')len
binaray_whereis = '/usr/bin/whereis'

class FileManager:
	def __init__(self):
		if os.path.exists(binaray_whereis):
			if not os.path.isfile(binaray_whereis): 
				Log1.Logger.error('바이너리 파일이 아닙니다: %s' %binaray_whereis)
		else:
			Log1.Logger.error('바이너리 파일이 존재하지 않습니다: %s' %binaray_whereis)
		pass
	def ls(self, *args, **kwargs):
		paramiter = {
			'ext' : None
		}
		list 	= ''

		paramiter.update(kwargs)

		if len(args) == 0:
				list = os.listdir('.')
		else: 
			find_to_path = args[0]
			if os.path.exists(find_to_path):
				list = os.listdir(find_to_path)
			else:
				Log1.Logger.error('폴더를 읽을 수 없습니다: %s' %find_to_path)
				return 'error'

		if paramiter['ext'] is not None:
			ext = paramiter['ext']
			list = [x for x in list if x.endswith('.%s' %ext)] 
		
		return list

	def mv(self, orig, dest):
		if os.path.exists(orig): 
			os.rename(orig, dest)
		else: 
			Log1.Logger.error('이동시킬 파일이 없습니다 From:%s To:%s' %(orig, dest))
			return False

		if os.path.exists(dest):
			return True
		else:
			Log1.Logger.error('파일 변환에 실패합니다. From:%s To:%s' %(orig, dest))
			return False

	def cp(self, orig, dest, **kwargs):
		paramiter = {
			'none' : None
		}

		shutil.copy (orig, dest)
		if os.path.exists(dest):
			return True
		else:
			Log1.Logger.error('파일 복사에 실패합니다. From:%s To:%s' %(orig, dest))
			return False

	def mkdir(self, path):
		if os.path.exists(path):
			return True
		os.makedirs(path)
		if os.path.exists(path):
			return True
		else:
			Log1.Logger.error('디렉토리 만들기에 실패합니다. 경로:%s' %(path))
			return False

	def exists(self, path):
		if os.path.exists(path): 
			return True
		else: 
			return False

	def exist(self, path):
		return os.path.exists(path)

	def rm(self, path):
		if os.path.exists(path): 
			os.remove(path)
			if not os.path.exists(path): 
				return True
			else:
				Log1.Logger.error('파일 삭제에 실패합니다. 경로:%s' %(path))
				return False
		else:
			return False
			Log1.Logger.error('삭제할 파일이 없습니다. 경로:%s' %(path))

	def binnary_file(self, path):
		pass
		#subprocess



