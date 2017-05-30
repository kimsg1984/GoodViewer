#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: SunGyo Kim
# Email: Kimsg1984@gmail.com
# irc.freenode #ubuntu-ko Sungyo


import wx

import Data.WildCard
wildcard = Data.WildCard.getKeywords()
wildcard_on_dialog = "Imaeg File (*.jpg;*.png..)|%s| All files (*.*)|*.*" %(wildcard[0])

class FileDialog(wx.FileDialog):
	def __init__(self, parent):
		wx.FileDialog.__init__(self, parent, "Choose a file",
		wildcard=wildcard_on_dialog,
		style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR)
