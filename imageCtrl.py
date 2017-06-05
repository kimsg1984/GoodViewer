#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: SunGyo Kim
# Email: Kimsg1984@gmail.com
# irc.freenode #ubuntu-ko Sungyo

import os
import re
import wx
import StringIO
import urllib2
import sys
import random
reload(sys)

## 커스텀 모듈 ####
pymodule_path='/home/sungyo/Unison/script/module/python'
sys.path.append(pymodule_path)
# sys.path.append('../') # for debuging

import IO
Config = IO.Shelve(filename='./Data/gooviewer_config.dat')
Log	= IO.Log(log_name='ImageCtrl', filelogging=False)

import TRASH
Trash = TRASH.Trash()

#################

import Data.WildCard
wildcard = Data.WildCard.getKeywords()
wildcard_on_listdir = wildcard[1]

class ImageCtrl():
	def __init__(self):
		self.__setClassValues()

	def __setClassValues(self):
		self.throwed_file = []
		self.wildcard = '.(%s)' %wildcard_on_listdir
		self.which_way_to_go 	= True
		self.folder_flip 		= False
		self.should_flip_folder 	= False
		self.setClassValuesDefauts()

	def setClassValuesDefauts(self):
		self.pic_files 	= []
		self.pic_dir 	= ''
		self.current_filename = ''

		self.current_num = 0
		self.next_num 	= 0
		self.pre_num 	= 0
		self.total_pictures= 0

		self.current_img 	= None
		self.next_img 	= None
		self.pre_img 	= None

	def _get_CurrentFileName(self):
		if self.pic_files:
			filename = self.pic_files[self.current_num]
			return filename
		else:
			return False

	def _get_CurrentDir(self):
		if self.pic_dir: return self.pic_dir
		else: return False

	## WORK FUNCTION ##

	def filePathFromPicNumber(self, number):
		file_name = self.pic_files[number]
		file_path = os.path.join(self.pic_dir, file_name)
		return file_path

	def deleteImage(self): 
		current_path = os.path.join(self.pic_dir, self.pic_files[self.current_num])
		current_path = str(unicode(current_path))
		current_path_incoded = urllib2.quote(current_path)
	
		if not Trash.put(current_path): return None
		self.throwed_file.append(current_path)
		
		if 1 < self.total_pictures:
			if self.which_way_to_go: next_num = self.nextPicGettingNum(self.current_num)
			else : next_num = self.previousPicGettingNum(self.current_num)
			next_pic_path = self.filePathFromPicNumber(next_num)
			self.updateImages(next_pic_path)
		else:
			if self.folder_flip:
				self.nextFolder()
			else:
				self.setClassValuesDefauts()
		return True

	def restoreImage(self):
		if self.throwed_file:
			restore_file_name = self.throwed_file.pop()
			restore_file_path = os.path.join(self.pic_dir, restore_file_name)
			if Trash.search(restore_file_path):
				file_name_in_trash = Trash.search(restore_file_path)[0][1]
				Trash.restore(file_name_in_trash)
				
				self.updateImages(restore_file_path) # 이미지 가져와서 던질것!!!
			else: return False
		else: return False

	def loadImage(self):
		"""
		이미지 불러오기, next Picture와 previous Picture 처리
		"""
		number 	= self.current_num

		if len(self.pic_files) is 0:
			if self.folder_flip:
				if self.which_way_to_go:
					self.nextFolder()
				else:
					self.previousFolder()

		filename 	= self.pic_files[number]
		self.current_filename = filename
		
		# print filename
		if not self.current_img : self.current_img = self.gettingImgForPanel(filename)

		# self.imageOnPanel(self.current_img)
		return self.current_img
		## second, prepare the Previous and Next pictures ##

	def gettingImgForPanel(self, filename):
		## class instance 
		dir = self.pic_dir
		image_path = os.path.join(dir, filename)
		if wx.Image.CanRead(filename=image_path):
			img = wx.Image(name=image_path)
		else:
			img = wx.EmptyImage(200, 200)
		return img

	def preparePictures(self):
		"""
		next_picture  와 pre_picture 불러놓기
		"""
		## class instance ##
		next_pic_path 	= self.pic_files[self.next_num]
		pre_pic_path 	= self.pic_files[self.pre_num]

		if not self.next_img : self.next_img = self.gettingImgForPanel(next_pic_path)
		if not self.pre_img : self.pre_img = self.gettingImgForPanel(pre_pic_path) 
		
		return True

	def nextPicture(self):
		"""
		Loads the next picture in the directory
		"""
		if self.folder_flip is True:
			if self.current_num == self.total_pictures - 1:
				if self.total_pictures > 1:
					self.nextFolder()
					return True

			if self.total_pictures is 1:
				self.nextFolder()
				return True

		self.pre_num, self.current_num, self.next_num = self.current_num, self.next_num, self.nextPicGettingNum(self.next_num)
		self.pre_img, self.current_img, self.next_img = self.current_img, self.next_img, None
		self.which_way_to_go = True

		return True

	def nextPicGettingNum(self, current_num):
		if current_num == self.total_pictures - 1:
			next_num = 0
		else:
			next_num = current_num + 1

		return next_num

	def previousPicture(self):
		"""
		Displays the previous picture in the directory
		"""
		if self.folder_flip is True:
			if self.current_num == 0:
				if self.total_pictures is not 1:
					self.previousFolder()
					return True

			if self.total_pictures is 1:
				self.previousFolder()
				return True

		self.pre_num, self.current_num, self.next_num = self.previousPicGettingNum(self.pre_num), self.pre_num, self.current_num
		self.pre_img, self.current_img, self.next_img = None, self.pre_img, self.current_img
		self.which_way_to_go = False

		
		return True

	def previousPicGettingNum(self, current_num):
		if current_num == 0:
			pre_num = self.total_pictures - 1
		else:
			pre_num = current_num - 1
		return pre_num

	def nextFolder(self): 
		dir = os.path.dirname(self.pic_dir)
		dir_name = os.path.split(dir)[-1]
		dir_parent = os.path.split(dir)[0]
		for f in os.walk(dir_parent): 
			dir_list = f[1]
			break
		dir_list.sort()
		dir_index = dir_list.index(dir_name)
		dir_len = len(dir_list)
		count = 0
		while count <= dir_len -1:
			dir_index += 1
			count += 1
			if dir_index >= dir_len :
				dir_index = 0
			next_dir = os.path.join(dir_parent, dir_list[dir_index])
			next_dir_list = os.listdir(next_dir)
			pic_files = []
			for l in next_dir_list:
				if len(re.findall(r'%s$' %(self.wildcard),l)) > 0:
					# print(os.path.join(next_dir, l))
					pic_files.append(l)
			
			if len(pic_files) > 0:
				count = dir_len
				pic_files.sort()
				self.updateImages(os.path.join(next_dir, pic_files[0]))

	def previousFolder(self): 
		dir = os.path.dirname(self.pic_dir)
		dir_name = os.path.split(dir)[-1]
		dir_parent = os.path.split(dir)[0]
		for f in os.walk(dir_parent): 
			dir_list = f[1]
			break
		dir_list.sort()
		dir_index = dir_list.index(dir_name)
		dir_len = len(dir_list)
		count = 0
		while count <= dir_len -1:
			dir_index -= 1
			count += 1
			if dir_index == 0 :
				dir_index = dir_len -1
			next_dir = os.path.join(dir_parent, dir_list[dir_index])
			next_dir_list = os.listdir(next_dir)
			pic_files = []
			for l in next_dir_list:
				if len(re.findall(r'%s$' %(self.wildcard),l)) > 0:
					pic_files.append(l)

			if len(pic_files) > 0:
				count = dir_len
				pic_files.sort()
				self.updateImages(os.path.join(next_dir, pic_files[-1]))

	def updateImages(self, file_path):
		"""
		Updates the pic_files list to contain the current folder's images
		"""
		self.setClassValuesDefauts()
		index_file = file_path.split('/')[-1]
		folder_path = file_path.split(index_file)[0]
		self.pic_dir = folder_path
		self.pic_files = []

		for l in os.listdir(self.pic_dir):
			if len(re.findall(r'%s$' %(self.wildcard),l)) > 0:
				Log.Logger.debug(re.findall(r'%s$' %(self.wildcard),l))
				self.pic_files.append(l)

		Log.Logger.debug(self.pic_files)
		self.pic_files.sort()
		self.total_pictures = len(self.pic_files)

		self.current_num =self.pic_files.index(index_file)
		self.next_num = self.nextPicGettingNum(self.current_num)
		self.pre_num = self.previousPicGettingNum(self.current_num)
		return True

	def goOnNumber(self, number):
		if self.total_pictures == 0 : return False
		number = int(number)
		if 0 <= number < self.total_pictures:
			file_path = self.filePathFromPicNumber(number)
			if self.updateImages(file_path): return True
		else: return False

	def firstPicture(self):
		if self.total_pictures > 1: 
			if self.goOnNumber(0): return True

	def lastPicture(self):
		if self.total_pictures > 1: 
			if self.goOnNumber(self.total_pictures - 1): return True

	def restoreImage(self): 
		if self.throwed_file:
			restore_file_name = self.throwed_file.pop()
			restore_file_path = os.path.join(self.pic_dir, restore_file_name)
			if Trash.search(restore_file_path):
				file_name_in_trash = Trash.search(restore_file_path)[0][1]
				if Trash.restore(file_name_in_trash):
					print 'restored'
					self.updateImages(restore_file_path)
					return True
				else: return False
			else: return False
		else: return None

	def nextOrFirst(self):
		if self.folder_flip is True: return True
		if self.current_num == self.total_pictures - 1 : return False
		else: return True

	def onPrepare(self, event):
		"""
		prepare the nex and previous pictures. it makes faster.
		"""        
		self.preparePictures()
