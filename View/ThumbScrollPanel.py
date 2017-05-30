#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: SunGyo Kim
# Email: Kimsg1984@gmail.com
# irc.freenode #ubuntu-ko Sungyo

import os
import time
import sys
# import wx.lib.agw.thumbnailctrl as TC
import wx
pymodule_path='/home/sungyo/Unison/script/module/python'
sys.path.append(pymodule_path)

import TRASH
Trash = TRASH.Trash()

import IO
Config = IO.Shelve(filename='./Data/gooviewer_config.dat')

import BO.thumbnailctrl
TC = BO.thumbnailctrl

import Data.WildCard
wildcard = Data.WildCard.getKeywords()
wildcard_on_thumb = wildcard[2]

class SelectEvent():
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def GetX(self):
        return self.x

    def GetY(self):
        return self.y

    def Skip(self):
        pass

class ThumbScrollPanel(TC.ScrolledThumbnail):
    def __init__(self, parent, imageCtrl):
        TC.ScrolledThumbnail.__init__(self, parent)
        self.ImageCtrl = imageCtrl
        self.SetBackgroundColour('black')
        setattr(parent, 'RecreateComboBox', self.RecreateComboBox)
        self.parentClass = parent
        self.__setClassValues()
        self.__setScrollPanel()
        self.__binding()

        # self.showDir(u'/home/sungyo/100D5100')
        # self.showDir(u'/home/sungyo/다운로드/Save/$$MPL_Studios_Paloma_-_Treat_Me_Right__27_Jan_2015__x80x4000')

    def __setClassValues(self):
        self._dir = None
        self._selected_pictures = []
        self._remove_items = []
        self._updating = False

    def __setScrollPanel(self):
        self.ShowFileNames()
        self.SetDropShadow(False)
        self.SetHighlightPointed(True)

        if Config.hasKey('thumb_size'):
            thumb_size = Config.load('thumb_size')
            self.SetThumbSize(thumb_size[0], thumb_size[1])

        if Config.hasKey('thumb_panel_size'):
            print 'get size'
            self.parentClass.SetSize(Config.load('thumb_panel_size'))
        if Config.hasKey('thumb_panel_position'):
            print 'get pos'
            self.parentClass.SetPosition(Config.load('thumb_panel_position'))

    def __binding(self):

        self.Bind(TC.EVT_THUMBNAILS_POINTED, self.nonEvent)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnDClick)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseMove)
        self.Bind(wx.EVT_MOUSEWHEEL, self.onMouseWheel)

        self.Bind(wx.EVT_LEFT_UP, self.nonEvent)
        self.Bind(wx.EVT_RIGHT_DOWN, self.nonEvent)
        self.Bind(wx.EVT_RIGHT_UP, self.nonEvent)
        self.Bind(wx.EVT_MOTION, self.nonEvent)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.nonEvent)

    def _get_onUpdating(self):
        return self._on_updating

    def RecreateComboBox(self, folder):
        pass

    def nonEvent(self, event):
        pass

    def showDir(self, folder):
        # self.parentClass.Freeze()
        self._updating = True
        self.ShowDir(folder, extensions = wildcard_on_thumb)
        wx.MilliSleep(2000)
        self._updating = False
        self.SetFocus()

    def onDirectory(self):
        dlg = wx.DirDialog(self, "Choose A Directory With Images:",
                           defaultPath=os.getcwd(),
                           style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)

        if dlg.ShowModal() == wx.ID_OK:
            dir = dlg.GetPath()
            self.showDir(dir)

    def onDelete(self):
        print 'delete'
        self._selectedarray.sort()
        self._selectedarray.reverse()
        print 'self._selectedarray:', self._selectedarray
        if 0 < len(self._selectedarray):
            for f in self._selectedarray:
                item = self.GetItem(f)
                if item is None: continue
                if not Trash.put(item.GetFullFileName()): continue
                self._remove_items.append((item, f))
                self.RemoveItemAt(f)
        self._selectedarray = []
        self.Parent.Thaw()
        self.Refresh()

    def onUndo(self):
        self._selectedarray = []
        if 0 < len(self._remove_items):
            for i in self._remove_items:
                file_name_in_trash = Trash.search(i[0].GetFullFileName())[0][1]
                if not Trash.restore(file_name_in_trash): continue
                self.InsertItem(i[0], i[1])
                self._selectedarray.append(i[1])
        self._remove_items = []
        self.SortItems()
        self.Refresh()

    def OnDClick(self, event):
        if self._updating: return
        # print event.GetY()
        item_number = self.getItemNumber(event.GetX(), event.GetY())
        item = self.GetItem(item_number)
        filename = item.GetFullFileName()
        # print 'Dclicked', filename
        self.parentClass.switchToViewer(filename)

    def OnMouseDown(self, event):
        """
        Handles the ``wx.EVT_LEFT_DOWN`` and ``wx.EVT_RIGHT_DOWN`` events for L{ThumbnailCtrl}.

        :param `event`: a `wx.MouseEvent` event to be processed.
        """
        if self._updating: return
        x = event.GetX()
        y = event.GetY()
        x, y = self.CalcUnscrolledPosition(x, y)
        # get item number to select
        lastselected = self._selected
        self._selected = self.GetItemIndex(x, y)

        self._mouseeventhandled = False
        update = False

        if event.ControlDown():
            pass
            if self._selected == -1:
                self._mouseeventhandled = True

            else:
                if self.IsSelected(self._selected):
                    self._selectedarray.remove(self._selected)
                    update = True
                    self._mouseeventhandled = True
                else:
                    self._selectedarray.append(self._selected)
                    update = True
                    self._mouseeventhandled = True

        elif event.ShiftDown():
            if self._selected != -1:
                begindex = self._selected
                endindex = lastselected
                if lastselected < self._selected:
                    begindex = lastselected
                    endindex = self._selected

                for ii in xrange(begindex, endindex+1):
                    print 'ii: ', ii
                    if self.IsSelected(ii):
                        self._selectedarray.remove(ii)
                        print 'remove: ', ii
                    else: self._selectedarray.append(ii)

                update = True

            self._selected = lastselected
            self._mouseeventhandled = True

        else:
            print self._selected
            if self._selected == -1:
                update = len(self._selectedarray) > 0
                self._mouseeventhandled = True
            elif len(self._selectedarray) <= 1:
                try:
                    update = len(self._selectedarray) == 0 or self._selectedarray[0] != self._selected
                except:
                    update = True
                # self._selectedarray = []
                # self._selectedarray.append(self._selected)
                self._mouseeventhandled = True

        if update:
            print 'update: ', update
            self.ScrollToSelected()
            self.Refresh()
            eventOut = TC.ThumbnailEvent(TC.wxEVT_THUMBNAILS_SEL_CHANGED, self.GetId())
            self.GetEventHandler().ProcessEvent(eventOut)

        self.SetFocus()

    def OnRight(self):
        if self._updating: return
        if self._selected == -1:
            self.pointThumb(0)
            self._selected = 0
        elif self._selected < self.GetItemCount() -1 :
            self._selected = self._selected + 1
            self.pointThumb(self._selected)

    def OnLeft(self):
        if self._updating: return
        if 0 < self._selected :
            self._selected = self._selected - 1
            self.pointThumb(self._selected)

    def OnUpDown(self, key):
        if self._updating: return
        lines = self.GetItemCount() / self._cols
        current_line = 0
        print self._selected
        if self._selected is -1:
            self.pointThumb(0)
            return
        else:
            current_line = self._selected / self._cols

        if key == 'down'and current_line < lines :
            self.pointThumb(self._selected + self._cols)
        elif key == 'up' and 0 < current_line:
            self.pointThumb(self._selected - self._cols)

    def onSpaceBar(self):
        if self._updating: return
        if self._selected is not -1 : self.selectThumb(self._selected)

    def onEscape(self):
        if self._updating: return
        self._selectedarray = []
        self.Refresh()

    def onReturn(self):
        if self._updating: return
        if self._selected is not -1 :
            item = self.GetItem(self._selected)
            filename = item.GetFullFileName()
            self.parentClass.switchToViewer(filename)

    def onMouseWheel(self, event):
        if self._updating: return
        self.OnMouseWheel(event)
        if event.ControlDown():
            Config.save('thumb_size',(self.GetThumbSize()[0], self.GetThumbSize()[1]))

    def pointThumb(self, number):
        self._selected = number
        selectedarray = self._selectedarray
        self.SetSelection(number)
        self._selectedarray = selectedarray

        number_line = (number / self._cols)
        event_col = number - (number_line * self._cols)
        event_x = (event_col * (self._tWidth + self._tBorder)) + (self._tWidth / 2)
        event_y = ((self._tHeight + self._tBorder + self.GetCaptionHeight(0)) * number_line) + (self._tHeight / 2)
        unscrolled_x, unscrolled_y  = self.CalcScrolledPosition(event_x, event_y)
        event = SelectEvent(unscrolled_x,unscrolled_y)
        self.OnMouseMove(event)

    def selectThumb(self, number):
        if -1 < number < self.GetItemCount():
            if self.IsSelected(number):
                self._selectedarray.remove(number)
            else:
                self._selectedarray.append(number)
            self.Refresh()

    def getItemNumber(self, x, y):
        x, y = self.CalcUnscrolledPosition(x, y)
        return self.GetItemIndex(x, y)
