#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: SunGyo Kim
# Email: Kimsg1984@gmail.com
# irc.freenode #ubuntu-ko Sungyo

import wx
import View.Dialog
import StringIO
import urllib2
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import IO
Config = IO.Shelve(filename='./Data/gooviewer_config.dat')

import View.Dialog

class ViewerMenuBar():
	def __init__(self, parent, panel):
		self.parentClass = parent
		self.Panel = panel
		self.setMenuBar()

		self.__setClassValues()
		self.__loadConfig()

	def __setClassValues(self):
		self.folderPath = ""
		self._full_screen_state = False
		self._switch = False
		self._on_slide_state = False

	def  setMenuBar(self):

		def defineMenu(element_name):
			menu = wx.Menu()
			self.defineMenues.append((menu, element_name))
			return menu

		self.defineMenues = []
		self.bind_list = []

		## Setting up the menu ##
		
		def append(menu, bind_function, element_name, comment,  id = wx.ID_ANY, item = None):
			# 추가할 메뉴, 바인드함수, 라벨이름, 설명, (아이디와 아이템)
			# '라벨이름에 해당되는 'element_name'은 중복되서는 안된다.'

			if item: 	result = menu.Append(id, element_name, comment, item)
			else: 		result = menu.Append(id, element_name, comment)
			self.bind_list.append((bind_function, result))
			return result
		
		def subMenu(main_menu, element_name):
			sub_menu = wx.Menu()
       			main_menu.AppendMenu(wx.NewId(), element_name, sub_menu)
       			return sub_menu 

		comment = {
					'full_rotate_right' 	: "for Stand Picture, Rotate on Clockwise  on Full Screen",
					'full_rotate_left'		: "for Stand Picture, Rotate against Clockwise  on Full Screen",
					"high_quelity"		: "Getting High Image Quiliy",
					"slide_show"		: "Start Slide Show"
				} # for long comment..

		## Each MenuBar ############  
		
		# Open #
		fileMenu 			= defineMenu( '&File')
		bar_file_open 		= append(fileMenu, 	self.onOpen, 	"&Open", "Open the Image File and Directory", id = wx.ID_OPEN)
		bar_thumbnail_ctrl 	= append(fileMenu, 	self.onSwitchThumb, "&Thumbnail Ctrl\tCtrl+T", "Open the Thumbnail Controller")
		bar_exit			= append(fileMenu, 	self.onExit, 	"E&xit", "Close the Window", id = wx.ID_EXIT)
		
		# Edit #
		editMenu 			= defineMenu( '&Edit')
		bar_delete			= append(editMenu, 	self.onDelete, 	"&Delete\tDelete", "Going Trash", id = wx.ID_DELETE)
		bar_undo 			= append(editMenu, 	self.onUndo, 	"&Undo\tCtrl+Z", "Restore the Deleted Picture", id = wx.ID_UNDO)
		
		# View #
		viewMenu 					= defineMenu( '&View')
		self.bar_full_screen		= append(viewMenu, 	self.onFull_screen, "&Full Screen\tF11", "Show on Full Screen", item = wx.ITEM_CHECK)
		self.bar_folder_flip = append(viewMenu, 	self.onFolder_flip, "Folder F&lip\tAlt+L", "Folder Flip or Rotate", item = wx.ITEM_CHECK)

		viewMenu.AppendSeparator()
		self.bar_full_rotate_off	= append(viewMenu, 	self.onFull_rotate, "  N&one\tCtrl+Shift+N", "....", item = wx.ITEM_RADIO)
		self.bar_full_rotate_right= append(viewMenu, self.onFull_rotate, "  &Right\tCtrl+Shift+R", comment['full_rotate_right'], item = wx.ITEM_RADIO)
		self.bar_full_rotate_left = append(viewMenu, 	self.onFull_rotate, "  &Left\tCtrl+Shift+L", comment['full_rotate_left'], item = wx.ITEM_RADIO)

		viewMenu.AppendSeparator()
		self.zoom_in 		= append(viewMenu, 	self.onZoomIn, "Zoom In\tCtrl+=", 'Zoom In')
		self.zoom_out 		= append(viewMenu, 	self.onZoomOut, "Zoom Out\tCtrl+-", 'Zoom Out')
		self.zoom_fit 		= append(viewMenu, 	self.onZoomFit, "Fit on Window\t=", 'Fit on Window')
		# viewMenu.AppendSeparator()
		
		self.bar_high_quelity 	= append(viewMenu, 	self.onQuelity, "&High Quelity\tCtrl+Shift+H", comment["high_quelity"], item = wx.ITEM_CHECK)
		self.slide_show		= append(viewMenu, 	self.onSlideShow, "&Slide Show\tF5", comment['slide_show'], item = wx.ITEM_CHECK)
		# viewMenu.AppendSeparator()
		viewMenu.AppendSeparator()
		slide_show_config	= append(viewMenu, 	self.onConfiguration, "&Configuration..\tCtrl+Shift+P", comment['slide_show'])

		# Go #
		goMenu 			= defineMenu( '&Go')
		bar_next_pictur 		= append(goMenu, 	self.onNext_picture, "&Next Pic...\tRight", "Go on Next Picture")
		bar_previous_picture	= append(goMenu, 	self.onPrevious_picture, "&Previous Pic...\tLeft", "Go on Previous Picture")
		bar_first_picture 		= append(goMenu, 	self.onFirst_picture, "&First Pic...\tCtrl+F", "Go on First Picture")
		bar_last_picture 		= append(goMenu, 	self.onLast_picture, "&Last Pic...\tCtrl+L", "Go on Last Picture")
		
		# Help #
		helpMenu  			= defineMenu( '&Help' )
		bar_about 			= append(helpMenu, 		self.onAbout, 	"&About", 	"Information about this program", item = wx.ID_ABOUT)		

	def showMenuBar(self):
		for l in self.bind_list: self.parentClass.Bind(wx.EVT_MENU, l[0], l[1])

		## Creating the menubar ##
		self.menuBar = wx.MenuBar()
		for m in self.defineMenues : self.menuBar.Append(m[0], "%s  " %(m[1]))
		self.parentClass.SetMenuBar(self.menuBar)
		self.parentClass.Bind(wx.EVT_CHAR_HOOK, self.onKeyUP)

	def switch(self, value):
		self._switch = value 

	def __loadConfig(self):
		if Config.load('sub_high_quelity'): self.bar_high_quelity.Check()

		rotate_key = Config.load('full_rotate')
		if 	rotate_key == 'off'	: self.bar_full_rotate_off.Check()
		elif	rotate_key == 'left'	: self.bar_full_rotate_left.Check()
		elif 	rotate_key == 'right'	: self.bar_full_rotate_right.Check()

	## <MenuBar Function> ----------------------------------------------------------------------

	def openFile(self, filename):
		filename = urllib2.unquote(filename).decode('utf8')
		self.Panel.onUpdateImages(filename)

	def onOpen(self, event):
		dlg = View.Dialog.FileDialog(self.parentClass)
		if dlg.ShowModal() == wx.ID_OK:
			file_path = dlg.GetPath()
			self.Panel.onUpdateImages(file_path)
			dlg.Destroy()

	def onExit(self, event): 
		self.parentClass.Close(True)
		sys.exit()		

	def onNext_picture(self, event):
		self.Panel.onNextPicture()

	def onPrevious_picture(self, event):
		self.Panel.onPreviousPicture()

	def onFull_screen(self, event):
		if self._full_screen_state: # 현재 풀스크린 상황을 확인한다
			self.fullSceenState(False)
		else:
			self.fullSceenState(True)

	def onFolder_flip(self, event): 
		if self.bar_folder_flip.IsChecked(): 
			self.Panel.onFolderFlip(True)
		else:	
			self.Panel.onFolderFlip(False)


	def onFull_rotate(self, event):
		if self.bar_full_rotate_off.IsChecked():
			self.Panel._set_virticalScreenRotate('off')
			Config.save('full_rotate', 'off')
		else:
			if self.bar_full_rotate_right.IsChecked(): 
				self.Panel._set_virticalScreenRotate('right')
				Config.save('full_rotate', 'right')
			elif self.bar_full_rotate_left.IsChecked(): 
				self.Panel._set_virticalScreenRotate('left')
				Config.save('full_rotate', 'left')

		self.Panel.loadImage()

	def onQuelity(self, event):
		if self.bar_high_quelity.IsChecked(): 
			self.Panel._set_ImageQuelityHigh(True)
			Config.save('sub_high_quelity', True)
		else: 
			self.Panel._set_ImageQuelityHigh(False)
			Config.save('sub_high_quelity', False)
		self.Panel.loadImage()

	def onFirst_picture(self, event):
		self.Panel.onFirst_picture()

	def onLast_picture(self, event):
		self.Panel.onLast_picture()

	def onZoomIn(self, event):
		self.Panel.onZoomIn()

	def onZoomOut(self, event):
		self.Panel.onZoomOut()

	def onZoomFit(self, event):
		self.Panel.onZoomFit()

	def onDelete(self, event):
		self.Panel.onDeleteImage()

	def onUndo(self, event):
		self.Panel.onRestoreImage()

	def onSlideShow(self, event):
		if self._on_slide_state:
			self._on_slide_state = False
			self.slide_show.Check(False)
			self.Panel.onSlide(False)
		else:
			self._on_slide_state = True
			self.slide_show.Check(True)
			self.Panel.onSlide(True)
		# if self.slide_show.IsChecked():
			# self.Panel.onSlide()
		
	def onAbout(self, event):
		dlg = wx.MessageDialog(self, "A small Image Viewer", "About Good Viewer", wx.OK)
		dlg.ShowModal() 
		dlg.Destory() 

	def onConfiguration(self, event):
		self.Panel.onConfiguration()

	def onSwitchThumb(self, event):
		dir = self.Panel._get_CurrentDir()
		self.parentClass.switchToThumbnailCtrl(dir)

	# <MenuBar Function/> ----------------------------------------------------------------------

	# Commend Function #######
	def renewFileName(self):
		filename = self.Panel._get_CurrentFileName()
		if filename : self.parentClass.SetTitle(filename)

	def fullSceenState(self, value):
		if value:
			self._full_screen_state = True 	# 상황을 표기하고
			self.Panel._state_fullScreen(True)	# 패널에도 표기한 뒤에
			self.parentClass.ShowFullScreen(True) 	# 풀스크린!
		else:
			self._full_screen_state = False
			self.Panel._state_fullScreen(False)
			self.parentClass.ShowFullScreen(False)
	
	# Keyboard Ctrl #######
	def onKeyUP(self, event): # let's set the key function
		keyCode = event.GetKeyCode()
		if keyCode == wx.WXK_ESCAPE:    # ESC
			if self._full_screen_state:
				self.fullSceenState(False)
			else:
				if self._switch: self.parentClass.switchToThumbnailCtrl(); print 'switch'
				else: self.parentClass.Close() ; print 'close'

		elif keyCode == wx.WXK_RIGHT:
			self.onNext_picture(wx.EVT_MENU)

		elif keyCode == wx.WXK_LEFT:
			self.onPrevious_picture(wx.EVT_MENU)

		elif keyCode == wx.WXK_F11:
			self.onFull_screen()

		elif keyCode == wx.WXK_F5: # for slide show
			self.onSlide()
			# self.Panel.onSlide()