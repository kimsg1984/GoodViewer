
import wx
import wx.lib.sheet as sheet
# http://zetcode.com/wxpython/dialogs/

class Configure(wx.Frame):
    def __init__(self, parent, id, title):

        # nb.AddPage(self.sheet1, "Sheet1")
        # nb.AddPage(self.sheet2, "Sheet2")
        # nb.AddPage(self.sheet3, "Sheet3")
        # nb = wx.Notebook(self, -1, style=wx.NB_TOP)

        self.cfg = wx.Config('myconfig')
        if self.cfg.Exists('width'):
            w, h = self.cfg.ReadInt('width'), self.cfg.ReadInt('height')
        else:
            (w, h) = (250, 250)
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(w, h))

        wx.StaticText(self, -1, 'Width:', (20, 20))
        wx.StaticText(self, -1, 'Height:', (20, 70))
        self.sc1 = wx.SpinCtrl(self, -1, str(w), (80, 15), (60, -1), min=200, max=500)
        self.sc2 = wx.SpinCtrl(self, -1, str(h), (80, 65), (60, -1), min=200, max=500)
        wx.Button(self, 1, 'Save', (20, 120))

        self.Bind(wx.EVT_BUTTON, self.OnSave, id=1)
        self.statusbar = self.CreateStatusBar()
        self.Centre()

    def OnSave(self, event):
        self.cfg.WriteInt("width", self.sc1.GetValue())
        self.cfg.WriteInt("height", self.sc2.GetValue())
        self.statusbar.SetStatusText('Configuration saved, %s ' % wx.Now())


# class MyApp(wx.App):
#     def OnInit(self):
#         frame = MyFrame(None, -1, 'myconfig.py')
#         frame.Show(True)
#         self.SetTopWindow(frame)
#         return True

# app = MyApp(0)
# app.MainLoop()