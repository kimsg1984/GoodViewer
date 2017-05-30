#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: SunGyo Kim
# Email: Kimsg1984@gmail.com
# irc.freenode #ubuntu-ko Sungyo

import wx
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

## Application Module ##
import View.ViewerPanel
import View.ThumbScrollPanel
import MenuBar.ViewerMenuBar
import MenuBar.ThumbScrollMenuBar
import imageCtrl
title = "Good Viewer"

class ViewerFrame(wx.Frame):
	def __init__(self,parent, ImageCTRL):
		wx.Frame.__init__(self, None, title=title)
		self.ImageCtrl = ImageCTRL
		self.parentClass = parent
		self.SetMinSize((400, 400))
		self.ViewerPanel = View.ViewerPanel.ViewerPanel(self, self.ImageCtrl)
		self.ViewerMenuBar = MenuBar.ViewerMenuBar.ViewerMenuBar(self, self.ViewerPanel)
		self.ViewerPanel.Show()
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.ViewerPanel, 1, wx.GROW | wx.ALL)
		self.ViewerMenuBar.showMenuBar()
		self.SetSizer(self.sizer)
		self.Center()

	def show(self, filename = None, switch = False):
		if filename : self.ViewerMenuBar.openFile(filename)
		self.ViewerMenuBar.switch(switch)
		self.sizer.Fit(self)
		self.SetFocus()
		self.Show()

	def hide(self):
		self.Hide()

	def switchToThumbnailCtrl(self, dir = None):
		self.parentClass.activeThumbnailCtrl(dir)
		self.hide()

class ThumbnailCtrlFrame(wx.Frame):
	def __init__(self, parent, ImageCTRL):
		wx.Frame.__init__(self, None, title=title)
		self.ImageCtrl = ImageCTRL
		self.parentClass = parent
		self.ThumbScrollPanel = View.ThumbScrollPanel.ThumbScrollPanel(self, self.ImageCtrl)
		self.ThumbScrollMenuBar = MenuBar.ThumbScrollMenuBar.ThumbScrollMenuBar(self, self.ThumbScrollPanel)
		self.ThumbScrollMenuBar.showMenuBar()
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.ThumbScrollPanel, 1, wx.GROW | wx.ALL)
		self.SetSizer(self.sizer)

	def show(self, dir = None):
		self.SetFocus()
		if dir: self.ThumbScrollPanel.showDir(dir)
		self.Show()


	def hide(self):
		self.Hide()

	def switchToViewer(self, filename = None):
		self.parentClass.activeViewer(filename, switch = True)
		self.hide()
		# self.show()

class myApp(wx.PySimpleApp):
	def __init__(self):
		wx.PySimpleApp.__init__(self)
		self.ImageCtrl = imageCtrl.ImageCtrl()

	def activeViewer(self, filename=None, switch = False):
		try: self.Viewerframe.show(filename, switch)
		except AttributeError:
			self.Viewerframe = ViewerFrame(self, self.ImageCtrl)
			self.Viewerframe.show(filename, switch)
			self.Viewerframe.Center()

		try: self.ThumbnailCtrlFrame.hide()
		except AttributeError: pass

	def activeThumbnailCtrl(self, dir=None):
		try: self.ThumbnailCtrlFrame.show(dir)
		except AttributeError:
			print 'new'
			self.ThumbnailCtrlFrame = ThumbnailCtrlFrame(self, self.ImageCtrl)
			self.ThumbnailCtrlFrame.show(dir)

		try: self.Viewerframe.hide()
		except AttributeError: pass

if __name__ == "__main__":
	try:
		filename = sys.argv[1]
	except:
		filename=None
	app = myApp()
	# filename = '/home/sungyo/Unison/2016/신대원수업/1학기/공관복음/1.png'
	if filename:app.activeViewer(filename)
	else: app.activeThumbnailCtrl()
	app.MainLoop()