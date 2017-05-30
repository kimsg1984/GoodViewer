#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: SunGyo Kim
# Email: Kimsg1984@gmail.com
# irc.freenode #ubuntu-ko Sungyo


import wx
import sys
## 커스텀 모듈 ##

pymodule_path='/home/sungyo/Unison/script/module/python'
sys.path.append(pymodule_path)
import IO
Config = IO.Shelve(filename='./Data/gooviewer_config.dat')
# Config = IO.Shelve(filename='../Data/gooviewer_config.dat') # for debug

# http://zetcode.com/wxpython/dialogs/

class Configure(wx.Frame):
    def __init__(self, parent, id, title):
        (w, h) = (250, 130)
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(w, h))

        self.initial_min = Config.load('slide_time_min')
        self.initial_max = Config.load('slide_time_max')

        self.text1 = wx.StaticText(self, -1, 'Min:', (20, 20))
        self.text2 = wx.StaticText(self, -1, 'Max:', (20, 70))
        self.sc1 = wx.SpinCtrl(self, -1, str(w), (150, 15), (60, -1), min=1, max=900, initial=self.initial_min)
        self.sc2 = wx.SpinCtrl(self, -1, str(h), (150, 65), (60, -1), min=1, max=900,initial=self.initial_max)
        self.sc1.SetValue(self.initial_min)
        self.sc2.SetValue(self.initial_max)

        self.sc1.Bind(wx.EVT_TEXT, self.OnSC1)
        self.sc2.Bind(wx.EVT_TEXT, self.OnSC2)
        self.Bind(wx.EVT_CHAR_HOOK, self.onKeyUP)
        self.Centre()
        self.sc1.SetFocus()

    def save(self):
        Config.save('slide_time_min', self.initial_min)
        Config.save('slide_time_max', self.initial_max)
        print Config.load('slide_time_max'), Config.load('slide_time_min')

    def OnSC1(self, event):
        self.initial_min = self.sc1.GetValue()
        self.sc2.SetRange (self.initial_min, 900)
        self.save()

    def OnSC2(self, event):
        self.initial_max = self.sc2.GetValue()
        self.sc1.SetRange (1, self.initial_max)
        self.save()

    def ShowOn(self, slide_time_min, slide_time_max):
        self.initial_min = slide_time_min
        self.initial_max = slide_time_max
        self.Show(True)

    def onKeyUP(self, event):
        keyCode = event.GetKeyCode()

        if keyCode == wx.WXK_ESCAPE:    # ESC
            self.save()
            self.Close()