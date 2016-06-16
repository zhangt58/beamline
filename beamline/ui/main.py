#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This is a demo:
    1: UI generated from wxFormBuilder
    2: event bindings are implemented later

Tong Zhang
2016-05-27 15:54:59 PM CST
"""

import myappframe
import wx


def run():
    app = wx.App()
    frame = myappframe.MyAppFrame(None, 'Lattice Viewer')
    frame.SetSize((1024, 768))
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    run()
