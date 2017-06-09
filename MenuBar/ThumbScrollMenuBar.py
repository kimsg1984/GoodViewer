#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: SunGyo Kim
# Email: Kimsg1984@gmail.com
# irc.freenode #ubuntu-ko Sungyo

import sys
import urllib2
import wx

reload(sys)
sys.setdefaultencoding('utf-8')

pymodule_path='/home/sungyo/Unison/script/module/python'
sys.path.append(pymodule_path)

import IO
Config = IO.Shelve(filename='./Data/gooviewer_config.dat')

class ThumbScrollMenuBar():
	def __init__(self, parent, panel):
		self.Parent = parent
		self.Panel = panel
		
		self.__setClassValues()
		self.__setFileHistory()
		self.setMenuBar()
		self.__loadConfig()

	def __setClassValues(self):
		self.class_value = ""
		pass

	def __setFileHistory(self):
		self.filehistory = wx.FileHistory(5)
		self.history_config = wx.Config("Good Viewer", style=wx.CONFIG_USE_LOCAL_FILE)
		self.filehistory.Load(self.history_config)
		

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
			if bind_function:	self.bind_list.append((bind_function, result))
			return result

		def subMenu(main_menu, element_name, sub_menu = None):
			if not sub_menu: sub_menu = wx.Menu()
       			main_menu.AppendMenu(wx.NewId(), element_name, sub_menu)
       			return sub_menu 

		comment = {
			'menubar_name' 	: "comment"
		} # for long comment..

		## Each MenuBar ############  

		# set filehistory
		bar_recent_files = wx.Menu()
		self.filehistory.UseMenu(bar_recent_files)
		self.filehistory.AddFilesToMenu() # add files to menu

		# File #
		fileMenu 			= defineMenu( '&File')
		bar_file_open 		= append(fileMenu, 	self.onOpen, 	"&Open", "Open the Image File and Directory", id = wx.ID_OPEN)
		bar_recent_files 		= subMenu(fileMenu, "&Recent Files", bar_recent_files)
		bar_exit			= append(fileMenu, 	self.onExit, 		"E&xit", "Close the Window", id = wx.ID_EXIT)

		# Edit #
		editMenu			= defineMenu('&Edit')
		bar_delete			= append(editMenu, 	self.onDelete, 	"&Delete File \tDelete", "Going Trash", id = wx.ID_DELETE)
		bar_undo 			= append(editMenu, 	self.onUndo, 	"&Undo\tCtrl+Z", "Restore the Deleted Picture", id = wx.ID_UNDO)

		# Help #
		helpMenu  			= defineMenu( '&Help' )

	def showMenuBar(self):
		for l in self.bind_list: self.Parent.Bind(wx.EVT_MENU, l[0], l[1])
		# RecentFiles Binding
		self.Parent.Bind(wx.EVT_MENU_RANGE, self.onRecentFiles, id=wx.ID_FILE1, id2=wx.ID_FILE9)

		## Creating the menubar ##
		self.menuBar = wx.MenuBar()
		for m in self.defineMenues : self.menuBar.Append(m[0], "%s  " %(m[1]))
		self.Parent.SetMenuBar(self.menuBar)

		self._setEventBind()

	def closeMenuBar(self):
		self.Parent.Unbind(wx.EVT_MENU)
		self.Parent.Unbind(wx.EVT_CHAR_HOOK)


	def _setEventBind(self):
		self.Parent.Bind(wx.EVT_CHAR_HOOK, self.onKeyUP)

	def __loadConfig(self):
		# if Config.load('sub_high_quelity'): self.bar_high_quelity.Check()
		pass

	## <MenuBar> ----------------------------------------------------------------------

	def onOpen(self, event):
		if self.Panel._get_onUpdating is True: return
		self.Panel.onDirectory()

	def onExit(self, event):
		if self.Panel._get_onUpdating is True: return
		Config.save('thumb_panel_size', self.Parent.GetSize())
		Config.save('thumb_panel_position', self.Parent.GetScreenPosition())
		self.Parent.Close(True)
		sys.exit()

	def onDelete(self, event):
		if self.Panel._get_onUpdating is True: return
		print 'delete'
		self.Panel.onDelete()

	def onUndo(self, event):
		if self.Panel._get_onUpdating is True: return
		self.Panel.onUndo()

	def onResize(self, event):
		if self.Panel._get_onUpdating is True: return
		print self.Parent.GetSize()

	def onMove(self, event):
		pass

	def openFile(self, filename):
		filename = urllib2.unquote(filename).decode('utf8')
		self.Parent.switchToViewer(filename)
		# self.Panel.onUpdateImages(filename)

	def onRecentFiles(self, event): 
		file_num = event.GetId() - wx.ID_FILE1
		file_path = self.filehistory.GetHistoryFile(file_num)
		self.openFile(file_path)

	# # <MenuBar/> ----------------------------------------------------------------------

	def onKeyUP(self, event): # let's set the key function
		keyCode = event.GetKeyCode()
		if keyCode == wx.WXK_ESCAPE:    # ESC
			self.Panel.onEscape()
		elif keyCode == wx.WXK_RIGHT:
			self.Panel.OnRight()
		elif keyCode == wx.WXK_LEFT:
			self.Panel.OnLeft()
		elif keyCode == wx.WXK_UP: self.Panel.OnUpDown('up')
		elif keyCode == wx.WXK_DOWN: self.Panel.OnUpDown('down')
		elif keyCode == wx.WXK_SPACE: self.Panel.onSpaceBar()
		elif keyCode == wx.WXK_RETURN: self.Panel.onReturn()
		elif keyCode == wx.WXK_DELETE: self.Panel.onDelete()
