#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: SunGyo Kim
# Email: Kimsg1984@gmail.com
# irc.freenode #ubuntu-ko Sungyo

import wx
import sys
import random
import subprocess
import re
import os

reload(sys)
sys.setdefaultencoding('utf-8')
temporary_folder = os.path.expanduser('~/Temporary')

## 커스텀 모듈 ##
pymodule_path='/home/sungyo/Unison/script/module/python'
sys.path.append(pymodule_path)
# sys.path.append('../')
import IO
Config = IO.Shelve(filename='./Data/gooviewer_config.dat')
File = IO.File()
Log	= IO.Log(log_name='ViewerPanel', filelogging=False)

import OS
FileManager = OS.FileManager()

import View.Configure
import Data.WildCard
wildcard = Data.WildCard.getKeywords()
wildcard_on_listdir = wildcard[1]



# import self.ImageCtrl
# ImageCtrl = self.ImageCtrl.ImageCtrl()

# class ViewerPanel(wx.Panel):
class ViewerPanel(wx.ScrolledWindow):
	def __init__(self, parent, imageCtrl):

		wx.ScrolledWindow.__init__(self, parent)
		self.ImageCtrl = imageCtrl
		width, height = wx.DisplaySize()
		# Log.Logger.info('width, height: %s * %s' %(width, height))
		self.photo_max_size = height - 200
		self.window_size = (height - 200, height - 200)
		self.SetBackgroundColour('black')
		self.__setLayout()
		self.__setClassValues()
		self.__setPreViewingControlEvent()
		self.__setSlideTimerEvent()
		self.__loadConfig()
		self.__setRightCickPopup()
		self.binding()
		self.SetFocus()

	def __setLayout(self):
		self.empty_img	= wx.EmptyImage(self.photo_max_size,self.photo_max_size)
		self.canvus 	= wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(self.empty_img))
		self.Refresh()

	def __setClassValues(self):
		self.current_img = None
		self._full_screen_state = False
		self._set_virtical_screen_rotate = False
		self._rotate_clockwise = True
		self._set_image_quelity_high = False
		self._zooming = False
		self._drag_on = False
		self.setZoomDefault()

		self.bind_list = [
			(self, wx.EVT_SIZE, self.onResize),
			(self, wx.EVT_LEFT_DOWN, self.onPreviousPicture),
			(self.canvus, wx.EVT_LEFT_DOWN, self.onLeftDown),
			(self.canvus, wx.EVT_RIGHT_DOWN, self.onRightDown),
			(self.canvus, wx.EVT_LEFT_UP, self.onLeftUp),
			(self.canvus, wx.EVT_MOTION, self.onMotion)
			]

	def __loadConfig(self):
		rotate_key = Config.load('full_rotate')
		if rotate_key == 'off' : pass

		elif rotate_key == 'left'	:
			self._set_virtical_screen_rotate = True
			self._rotate_clockwise = False

		elif rotate_key == 'right':
			self._set_virtical_screen_rotate = True
			self._rotate_clockwise = True

		self._set_image_quelity_high = Config.load('sub_high_quelity')

	def __setPreViewingControlEvent(self):
		self.prepare_triger = wx.Timer()
		self.prepare_triger.Bind(wx.EVT_BUTTON, self.ImageCtrl.onPrepare)
		self.evt = wx.CommandEvent()
		self.evt.SetEventType(wx.EVT_BUTTON.typeId)

	def __setSlideTimerEvent(self):
		self.slideTimer = wx.Timer(None)
		self.slideTimer.Bind(wx.EVT_TIMER, self.nextSlide)
		if not Config.hasKey('slide_time_min'): Config.save('slide_time_min', 10)
		if not Config.hasKey('slide_time_max'): Config.save('slide_time_max', 10)

	def __setRightCickPopup(self):
		# RightCickPopup 
		menu_titles = [ 
			"Open Folder",
			"Open Webpage",
			"Copy to Temporary",
			]

		self.menu_title_by_id = {}

		for title in menu_titles:
		    self.menu_title_by_id[ wx.NewId() ] = title

	def _state_fullScreen(self, state):
		self._full_screen_state = state

	def _get_CurrentFileName(self):
		return self.ImageCtrl._get_CurrentFileName()

	def _get_CurrentDir(self):
		return self.ImageCtrl._get_CurrentDir()

	def _set_virticalScreenRotate(self, config):
		if 	config == 'off':
			self._set_virtical_screen_rotate = False

		elif 	config == 'right':
			self._set_virtical_screen_rotate = True
			self._rotate_clockwise = True

		elif 	config == 'left':
			self._rotate_clockwise = False
			self._set_virtical_screen_rotate = True

	def _set_ImageQuelityHigh(self, value):
		self._set_image_quelity_high=value

	def binding(self, value = True):
		for b in self.bind_list: b[0].Bind(b[1], b[2])

	def setZoomDefault(self):
		self._zooming = False
		self.zoom_ratio = 1
		self.zoom_power = 1.2
		self.scroll_size = 0
		self.scroll_ratio = [0.5, 0.5]

		self.SetScrollbars(0,0,0,0)

	## WORK FUNCTION ##

	def blinkScreen(self):
		self.canvus 	= wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(self.empty_img))
		self.main_sizer.Add(self.canvus, 1, wx.GROW|wx.ALIGN_CENTER|wx.ALL, 5)
		self.Refresh()

	def reSize(self, size):
		self.window_size = size
		if not self._zooming :
			try:
				if self.current_img: self.imageOnPanel(self.current_img)
			except AttributeError: pass
		self.Refresh()

	def loadImage(self): # work
		self.setZoomDefault()
		self.current_img = self.ImageCtrl.loadImage()
		self.imageOnPanel(self.current_img)
		wx.PostEvent(self.prepare_triger, self.evt)

	def imageOnPanel(self, img):

		## class instance ##
		window_size = self.window_size

		## Inter Function ####
		def fullScreenRotate(img):
			if self._full_screen_state:
				if self._set_virtical_screen_rotate:
					if img.GetWidth() < img.GetHeight() : # is the image wide or stand?
						img = img.Rotate90(clockwise=self._rotate_clockwise) # lay on right
			return img

		###################

		## full screen rotate ##
		img = fullScreenRotate(img)

		picture_w = img.GetWidth()
		picture_h = img.GetHeight()
		window_w, window_h = window_size[0], window_size[1]
		if ((float(window_w) / picture_w ) * picture_h ) <= window_h :  # which is fitter? w? or h?
			new_w = window_w
			new_h = int((float(new_w) / picture_w ) * picture_h)
		else:
			new_h = window_h
			new_w = int((float(new_h) / picture_h ) * picture_w)

		######################
		unit = 1
		distence = 40
		pos = (0 , 0)

		if self._zooming:
			new_w, new_h = new_w*self.zoom_ratio, new_h*self.zoom_ratio
			scroll_size = self.scroll_size
			scroll_ratio = self.scroll_ratio

			if 1 < self.zoom_ratio :
				## get class values ##
				view_start = self.GetViewStart()

				if view_start[0] is not 0: scroll_ratio[0] = view_start[0] / float(scroll_size[0] - window_size[0])
				if view_start[1] is not 0: scroll_ratio[1] = view_start[1] / float(scroll_size[1] - window_size[1])

				scroll_size = ((new_w/unit) + (distence*2), (new_h/unit) + (distence*2))
				pos = ((scroll_size[0] - window_size[0])*scroll_ratio[0], (scroll_size[1] - window_size[1])*scroll_ratio[1])

			else:
				scroll_size = (0, 0)

			self.SetScrollbars(unit, unit, scroll_size[0], scroll_size[1])

			## return class values ##
			self.scroll_size = scroll_size

		## Scale with Set Quelity ###
		if self._set_image_quelity_high: img = img.Scale(new_w, new_h, wx.IMAGE_QUALITY_HIGH)
		else: img = img.Scale(new_w, new_h)

		if 1 < self.zoom_ratio:
			control_position_w = distence
			control_position_h = distence

		else: # put center
			control_position_w = int((window_w - new_w) / 2)
			control_position_h = int((window_h - new_h) / 2)

		self.canvus.SetBitmap(wx.BitmapFromImage(img))
		self.canvus.SetPosition((control_position_w, control_position_h))
		self.Scroll(pos[0], pos[1])
		# self.refreshPanel()
		filename = self.ImageCtrl._get_CurrentFileName()
		if filename : self.Parent.SetTitle(filename)
		self.Refresh()

	def nextSlide(self, event):

		time = random.randrange(Config.load('slide_time_min'), int(Config.load('slide_time_max')) + 1) # 랜덤 맥스는 '%d 미만'으로 받는다
		# Log.Logger.debug('time: %s' %time)

		if self.slideTimer.IsRunning(): 
			if self.ImageCtrl.nextOrFirst() : self.onNextPicture()
			else: self.onFirst_picture()
			self.slideTimer.Stop()
			self.slideTimer.Start(time*1000) # 100 is a second
		else:
			self.slideTimer.Start(time*1000)

	def onResize(self, event):
		size = self.Parent.GetSize()
		self.reSize(size)

	def onLeftDown(self, event):
		if self._zooming:
			scroll_pos = self.GetViewStart()
			mouse_pos = event.GetPosition()
			self._drag_on = (mouse_pos[0] + scroll_pos[0] ,mouse_pos[1] + scroll_pos[1])
		else:self.onNextPicture()
	
	def onRightDown(self, event): 
		# record what was clicked
		# self.list_item_clicked = right_click_context = event.GetText()

		### 2. Launcher creates wxMenu. ###
		menu = wx.Menu()
		for (id,title) in self.menu_title_by_id.items():
			### 3. Launcher packs menu with Append. ###
			menu.Append( id, title )
			### 4. Launcher registers menu handlers with EVT_MENU, on the menu. ###
			wx.EVT_MENU( menu, id, self.onRightClickMenuSelection )

		### 5. Launcher displays menu with call to PopupMenu, invoked on the source component, passing event's GetPoint. ###
		self.PopupMenu( menu, event.GetPosition() )
		menu.Destroy() # destroy to avoid mem leak

	def onMotion(self, event):
		if self._drag_on is False: return
		moving_pos = event.GetPosition()
		x, y = self._drag_on[0] - moving_pos[0], self._drag_on[1] - moving_pos[1]
		self.Scroll(x, y)

	## Commend Function #########

	def onLeftUp(self, event):
		self._drag_on = False

	def onNextPicture(self, event = None):
		if self.ImageCtrl.nextPicture(): self.loadImage()

	def onPreviousPicture(self, event = None):
		if self.ImageCtrl.previousPicture(): self.loadImage()

	def onFolderFlip(self, folder_flip, event = None):
		self.ImageCtrl.folder_flip = folder_flip

	def onUpdateImages(self, file_path):
		result = self.ImageCtrl.updateImages(file_path)
		if result : self.loadImage()

	def onFirst_picture(self):
		if self.ImageCtrl.firstPicture(): self.loadImage()

	def onLast_picture(self):
		if self.ImageCtrl.lastPicture(): self.loadImage()

	def onDeleteImage(self):
		result = self.ImageCtrl.deleteImage()
		if result is not None:
			if result is True: 
				self.loadImage()
			else: 
				self.blinkScreen()

	def onRestoreImage(self):
		result = self.ImageCtrl.restoreImage()
		if result is not None:
			if result is True: self.loadImage()

	def onZoomIn(self):
		if self.current_img:
			self._zooming = True
			self.zoom_ratio = self.zoom_ratio*self.zoom_power
			self.imageOnPanel(self.current_img)

	def onZoomOut(self):
		if self.current_img:
			self._zooming = True
			self.zoom_ratio = self.zoom_ratio/self.zoom_power
			self.imageOnPanel(self.current_img)

	def onZoomFit(self):
		if self.current_img:
			self.setZoomDefault()
			self.imageOnPanel(self.current_img)

	def onSlide(self, check):
		if check:  self.nextSlide(wx.EVT_TIMER)  
		else: self.slideTimer.Stop()

	def onConfiguration(self):
		self.Configure = View.Configure.Configure(None, -1, 'Configuration')
		self.Configure.Show(True)

	## PopUp Menu Mathods #############
	def onRightClickMenuSelection(self, check):
		operation = self.menu_title_by_id[ check.GetId() ]
		print(operation)
		if operation == 'Open Folder': self.onOpenFolder()
		elif operation == 'Open Webpage': self.onOpenWebpage()
		elif operation == 'Copy to Temporary': self.onCopyToTemporary()

	def onOpenFolder(self):
		subprocess.check_call(['nautilus', self.ImageCtrl.pic_dir])

	def onOpenWebpage(self):
		pic_dir = self.ImageCtrl.pic_dir
		current_filename = self.ImageCtrl.current_filename
		
		# 20130930_1380468745_KIM_1941_2.jpg
		date_find = re.findall(r'^[0-9]{8}_', current_filename)
		if date_find:	
			for l in os.listdir(pic_dir):
				find_text = re.findall(r'^%s.+\.txt' %(date_find[0]) ,l)
				if len(find_text) > 0:
					address = (File.read(os.path.join(pic_dir, find_text[0])).split('\n'))[0] 
					subprocess.check_call(['chromium-browser', address])

	def onCopyToTemporary(self):
		print('copy')
		pic_dir = self.ImageCtrl.pic_dir
		current_filename = self.ImageCtrl.current_filename
		pic_file =  os.path.join( self.ImageCtrl.pic_dir, self.ImageCtrl.current_filename)
		dest_file = os.path.join(temporary_folder, current_filename)

		if not os.path.exists(temporary_folder):
			os.mkdir(temporary_folder)
			if not os.path.isdir(temporary_folder): 
				return False
				Log.Logger.error('Temporary folder를 생성하지 못하였습니다.')
		
		if not os.path.exists(dest_file): 
			FileManager.cp(pic_file, dest_file)