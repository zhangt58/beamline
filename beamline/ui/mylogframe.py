"""Subclass of LogFrame, which is generated by wxFormBuilder."""

# noinspection PyPackageRequirements
import wx
from . import appui


# Implementing LogFrame
class MyLogFrame(appui.LogFrame):
    def __init__(self, parent, log):
        appui.LogFrame.__init__(self, parent)
        self.show_log(log)

    def copy_btnOnButtonClick(self, event):
        input_text = self.log_tc.GetValue()
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(input_text))
            wx.TheClipboard.Close()

        dlg = wx.MessageDialog(self,
                               "Copy text to clipboard now, paste everywhere.",
                               "Data Copy Warning",
                               style=wx.ICON_WARNING | wx.OK | wx.CENTER)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()

    def exit_btnOnButtonClick(self, event):
        self.Close(True)

    def show_log(self, log):
        for line in log:
            if line['stat'] == 'OK':
                self.log_tc.SetDefaultStyle(wx.TextAttr("DARK GREEN"))
                self.log_tc.AppendText("{l}\n".format(l=line['logstr']))
            else:
                self.log_tc.SetDefaultStyle(wx.TextAttr("RED"))
                self.log_tc.AppendText("{l}\n".format(l=line['logstr']))
