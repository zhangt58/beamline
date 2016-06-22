#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
custom GUI controls

Tong Zhang
2016-06-19 12:37:40 PM CST
"""

import wx
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as Toolbar
from matplotlib.figure import Figure
import numpy as np
from bisect import bisect


class MyPlotPanel(wx.Panel):
    def __init__(self, parent, figsize=None, dpi=None, 
                 bgcolor=None, type=None, toolbar=None, aspect=1,
                 **kwargs):
        """ construction method of MyPlotPanel class
        :param parent: parent object
        :param figsize: plot figure size, (w, h)
        :param dpi: figure dpi,
        :parma bgcolor: background color of figure and canvas
        :param type: type of initial figure, 'image' or 'line'
        :param toolbar: show toolbar if not set None
        """
        wx.Panel.__init__(self, parent, **kwargs)
        self.parent = parent
        self.figsize = figsize
        self.dpi = dpi
        self.bgcolor = bgcolor
        self.type = type
        self.toolbar = toolbar
        self.aspect = aspect
        self.figure = Figure(self.figsize, self.dpi)
        self.canvas = FigureCanvas(self, -1, self.figure)

        # figure background color
        self.set_color(self.bgcolor)

        # initialize plot
        self._init_plot()

        # set layout
        self.set_layout()

        # binding events
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def set_layout(self):
        """ set panel layout
        """
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        if self.toolbar is not None:
            self.toobar = MyToolbar(self.canvas)
            self.toobar.Realize()
            hbox.Add(self.toobar, 0, wx.EXPAND | wx.RIGHT, 10)
        self.pos_st = wx.StaticText(self, label='')
        hbox.Add(self.pos_st, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(hbox, 0, wx.EXPAND | wx.BOTTOM, 0)
        self.SetSizerAndFit(sizer)

    def _init_plot(self):
        if not hasattr(self, 'axes'):
            self.axes = self.figure.add_subplot(111, aspect=self.aspect)
        if self.type == 'image':  # draw image
            x = y = np.linspace(-np.pi, np.pi, 100)
            self.x, self.y = np.meshgrid(x, y)
            self.z = self._func_peaks(self.x, self.y)
            self.image = self.axes.imshow(self.z)
        else: # draw line
            self.x = np.linspace(-10, 10, 200)
            self.y = np.sin(self.x)
            self.line, = self.axes.plot(self.x, self.y)

    def set_color(self, rgb_tuple):
        """ set figure and canvas with the same color.
        :param rgb_tuple: rgb color tuple, 
                          e.g. (255, 255, 255) for white color
        """
        if rgb_tuple is None:
            rgb_tuple = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE).Get()
        clr = [c/255.0 for c in rgb_tuple]
        self.figure.set_facecolor(clr)
        self.figure.set_edgecolor(clr)
        self.canvas.SetBackgroundColour(wx.Colour(*rgb_tuple))
        
    def on_size(self, event):
        self.fit_canvas()
        self.canvas.draw_idle()
        event.Skip()

    def on_press(self, event):
        pass

    def on_release(self, event):
        pass

    def on_motion(self, event):
        if event.inaxes is not None:
            self.pos_st.SetLabel("({x:<.4f}, {y:<.4f})".format(x=event.xdata, y=event.ydata))

    def fit_canvas(self):
        """ tight fit canvas layout
        """
        #self.canvas.SetSize(self.GetSize())
        self.figure.set_tight_layout(True)
        
    def _func_peaks(self, x, y):
        return 3.0 * (1.0 - x)**2.0 * np.exp(-(x**2) - (y+1)**2) \
             - 10*(x/5 - x**3 - y**5) * np.exp(-x**2-y**2) \
             - 1.0/3.0*np.exp(-(x+1)**2 - y**2)

class MyToolbar(Toolbar):
    def __init__(self, canvas):
        Toolbar.__init__(self, canvas)
        
        #self.AddTool(wx.ID_ANY, '')

class LatticePlotPanel(MyPlotPanel):
    def __init__(self, parent, **kwargs):
        MyPlotPanel.__init__(self, parent, **kwargs)

        #self.canvas.mpl_connect('pick_event', self.on_pick)
    
    #def on_pick(self, event):
    #    print event.mouseevent.xdata, event.mouseevent.ydata
    #    obj = event.artist
    #    if hasattr(self, 'anote_list'):
    #        for i in self.anote_list:

    def on_motion(self, event):
        if event.inaxes is not None:
            name, type = self.identify_obj(event.xdata)
            if name is not None:
                self.pos_st.SetLabel("({x:<.4f}, {y:<.4f}) --- [{name} : {type}]".format(
                    x=event.xdata, y=event.ydata,
                    name=name,type=type))
            else:
                self.pos_st.SetLabel("({x:<.4f}, {y:<.4f})".format(
                    x=event.xdata, y=event.ydata))
    
    def identify_obj(self, x):
        if self.x_pos_list is None: return None,None
        else:
            try:
                idx = bisect(self.x_pos_list, x)
                name = self.anote_list[idx]['name']
                type = self.anote_list[idx]['type']
            except IndexError:
                name, type = None, None
            return name, type


class TestFrame(wx.Frame):
    def __init__(self, parent, **kwargs):
        wx.Frame.__init__(self, parent, **kwargs)

        sizer = wx.BoxSizer(wx.VERTICAL)
        m_panel = MyPlotPanel(self, figsize=None, 
                               type='line', toolbar=True)
        sizer.Add(m_panel, 1, wx.ALIGN_CENTER | wx.EXPAND, 10)
        self.SetSizerAndFit(sizer)

def test():
    app = wx.App()
    frame = TestFrame(None, title="Matplotlib Panel Test")
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    test()
