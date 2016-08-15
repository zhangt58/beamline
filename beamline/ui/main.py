#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" GUI app of latticeviewer, 
    which is meant for accelerator online modeling,
    
    additional machine-related physics application should be implemented 
    and inserted into latticeviewer->Tools menu as a tool plugin.
    

Tong Zhang
2016-05-27 15:54:59 PM CST
"""

import myappframe
import wx


def run(debug=True, icon=None):
    app = wx.App()
    frame = myappframe.MyAppFrame(None, 
            u'Lattice Viewer \u2014 Accelerator Online Modeling Tool')
    frame.SetSize((1024, 768))
    frame.Show()
    if icon is not None:
        frame.SetIcon(icon)
    app.MainLoop()


if __name__ == '__main__':
    run()
