# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
from . import pltutils
import wx.richtext

###########################################################################
## Class MainFrame
###########################################################################


class MainFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self,
                          parent,
                          id=wx.ID_ANY,
                          title=wx.EmptyString,
                          pos=wx.DefaultPosition,
                          size=wx.Size(800, 600),
                          style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.Size(500, 300), wx.DefaultSize)

        vbox = wx.BoxSizer(wx.VERTICAL)

        control_hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.treename_st = wx.StaticText(self, wx.ID_ANY, u"Tree Name",
                                         wx.DefaultPosition, wx.DefaultSize, 0)
        self.treename_st.Wrap(-1)
        control_hbox.Add(self.treename_st, 0, wx.ALIGN_CENTER | wx.BOTTOM |
                         wx.TOP, 10)

        self.treename_tc = wx.TextCtrl(self, wx.ID_ANY, u"Lattice",
                                       wx.DefaultPosition, wx.DefaultSize,
                                       wx.TE_PROCESS_ENTER)
        control_hbox.Add(self.treename_tc, 1, wx.ALIGN_CENTER_VERTICAL |
                         wx.LEFT, 10)

        self.m_staticline1 = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition,
                                           wx.DefaultSize, wx.LI_VERTICAL)
        control_hbox.Add(self.m_staticline1, 0, wx.ALL | wx.EXPAND | wx.LEFT |
                         wx.RIGHT, 5)

        self.show_btn = wx.Button(self, wx.ID_ANY, u"&Show",
                                  wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.show_btn.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))
        self.show_btn.SetBackgroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOW))

        control_hbox.Add(self.show_btn, 0, wx.ALIGN_CENTER_VERTICAL, 10)

        self.generate_btn = wx.Button(self, wx.ID_ANY, u"&Generate",
                                      wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.generate_btn.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))
        self.generate_btn.SetBackgroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOW))

        control_hbox.Add(self.generate_btn, 0, wx.ALIGN_CENTER_VERTICAL |
                         wx.LEFT, 10)

        self.model_btn = wx.Button(self, wx.ID_ANY, u"&Model",
                                   wx.DefaultPosition, wx.DefaultSize, 0)
        control_hbox.Add(self.model_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT,
                         10)

        self.clear_btn = wx.Button(self, wx.ID_ANY, u"&Clear",
                                   wx.DefaultPosition, wx.DefaultSize, 0)
        self.clear_btn.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))
        self.clear_btn.SetBackgroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOW))

        control_hbox.Add(self.clear_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT,
                         10)

        self.exit_btn = wx.Button(self, wx.ID_ANY, u"E&xit",
                                  wx.DefaultPosition, wx.DefaultSize, 0)
        self.exit_btn.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))
        self.exit_btn.SetBackgroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOW))

        control_hbox.Add(self.exit_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT |
                         wx.RIGHT, 10)

        vbox.Add(control_hbox, 0, wx.EXPAND | wx.LEFT, 10)

        tree_hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.tree_splitter = wx.SplitterWindow(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D)
        self.tree_splitter.SetSashGravity(0.5)
        self.tree_splitter.Bind(wx.EVT_IDLE, self.tree_splitterOnIdle)
        self.tree_splitter.SetMinimumPaneSize(200)

        self.tree_left_panel = wx.Panel(self.tree_splitter, wx.ID_ANY,
                                        wx.DefaultPosition, wx.DefaultSize,
                                        wx.TAB_TRAVERSAL)
        tree_left_vbox = wx.BoxSizer(wx.VERTICAL)

        self.mainview_tree = wx.TreeCtrl(self.tree_left_panel, wx.ID_ANY,
                                         wx.DefaultPosition, wx.DefaultSize,
                                         wx.TR_DEFAULT_STYLE)
        tree_left_vbox.Add(self.mainview_tree, 1, wx.EXPAND | wx.LEFT, 10)

        self.tree_left_panel.SetSizer(tree_left_vbox)
        self.tree_left_panel.Layout()
        tree_left_vbox.Fit(self.tree_left_panel)
        self.tree_right_panel = wx.Panel(self.tree_splitter, wx.ID_ANY,
                                         wx.DefaultPosition, wx.DefaultSize,
                                         wx.TAB_TRAVERSAL)
        tree_right_vbox = wx.BoxSizer(wx.VERTICAL)

        self.nodeview_lc = wx.ListCtrl(
            self.tree_right_panel, wx.ID_ANY, wx.DefaultPosition,
            wx.DefaultSize, wx.LC_EDIT_LABELS | wx.LC_HRULES | wx.LC_REPORT |
            wx.LC_VRULES | wx.VSCROLL)
        tree_right_vbox.Add(self.nodeview_lc, 1, wx.EXPAND | wx.RIGHT, 10)

        self.tree_right_panel.SetSizer(tree_right_vbox)
        self.tree_right_panel.Layout()
        tree_right_vbox.Fit(self.tree_right_panel)
        self.tree_splitter.SplitVertically(self.tree_left_panel,
                                           self.tree_right_panel, 0)
        tree_hbox.Add(self.tree_splitter, 1, wx.EXPAND, 0)

        vbox.Add(tree_hbox, 1, wx.EXPAND, 10)

        bottom_hbox = wx.BoxSizer(wx.HORIZONTAL)

        search_hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.search_ctrl = wx.SearchCtrl(self, wx.ID_ANY, wx.EmptyString,
                                         wx.DefaultPosition, wx.DefaultSize,
                                         wx.TE_PROCESS_ENTER)
        self.search_ctrl.ShowSearchButton(True)
        self.search_ctrl.ShowCancelButton(True)
        search_hbox.Add(self.search_ctrl, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                        10)

        self.next_bmpbtn = wx.BitmapButton(
            self, wx.ID_ANY, wx.ArtProvider.GetBitmap(
                wx.ART_GO_DOWN, wx.ART_OTHER), wx.DefaultPosition,
            wx.DefaultSize, wx.BU_AUTODRAW)
        search_hbox.Add(self.next_bmpbtn, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                        10)

        self.previous_bmpbtn = wx.BitmapButton(
            self, wx.ID_ANY, wx.ArtProvider.GetBitmap(
                wx.ART_GO_UP, wx.ART_OTHER), wx.DefaultPosition,
            wx.DefaultSize, wx.BU_AUTODRAW)
        self.previous_bmpbtn.SetBackgroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOW))

        search_hbox.Add(self.previous_bmpbtn, 0, wx.ALIGN_CENTER_VERTICAL |
                        wx.RIGHT, 10)

        bottom_hbox.Add(search_hbox, 2, wx.EXPAND, 10)

        info_hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.action_st_panel = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition,
                                        wx.DefaultSize, wx.TAB_TRAVERSAL)
        action_st_panel_hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.action_st = wx.StaticText(self.action_st_panel, wx.ID_ANY,
                                       wx.EmptyString, wx.DefaultPosition,
                                       wx.DefaultSize, 0)
        self.action_st.Wrap(-1)
        self.action_st.SetForegroundColour(wx.Colour(0, 0, 0))
        self.action_st.SetBackgroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOW))

        action_st_panel_hbox.Add(self.action_st, 1, wx.ALIGN_CENTER | wx.ALL,
                                 5)

        self.action_st_panel.SetSizer(action_st_panel_hbox)
        self.action_st_panel.Layout()
        action_st_panel_hbox.Fit(self.action_st_panel)
        info_hbox.Add(self.action_st_panel, 1, wx.ALIGN_CENTER_VERTICAL |
                      wx.ALL | wx.EXPAND, 10)

        self.info_st = wx.StaticText(self, wx.ID_ANY, wx.EmptyString,
                                     wx.DefaultPosition, wx.DefaultSize,
                                     wx.ALIGN_LEFT)
        self.info_st.Wrap(-1)
        info_hbox.Add(self.info_st, 4, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT
                      | wx.ALL, 5)

        self.showlog_btn = wx.Button(
            self, wx.ID_ANY, u"...", wx.DefaultPosition, wx.Size(
                -1, -1), wx.BU_EXACTFIT | wx.NO_BORDER)
        info_hbox.Add(self.showlog_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT,
                      10)

        bottom_hbox.Add(info_hbox, 3, wx.EXPAND, 10)

        vbox.Add(bottom_hbox, 0, wx.EXPAND, 10)

        self.SetSizer(vbox)
        self.Layout()
        self.menu_bar = wx.MenuBar(0)
        self.file_menu = wx.Menu()
        self.open_mitem = wx.MenuItem(self.file_menu, wx.ID_OPEN,
                                      u"Open" + u"\t" + u"Ctrl+O",
                                      wx.EmptyString, wx.ITEM_NORMAL)
        self.file_menu.AppendItem(self.open_mitem)

        self.reopen_mitem = wx.MenuItem(self.file_menu, wx.ID_ANY,
                                        u"Reopen" + u"\t" + u"Ctrl+R",
                                        wx.EmptyString, wx.ITEM_NORMAL)
        self.file_menu.AppendItem(self.reopen_mitem)

        self.save_mitem = wx.MenuItem(self.file_menu, wx.ID_SAVE,
                                      u"Save" + u"\t" + u"Ctrl+S",
                                      wx.EmptyString, wx.ITEM_NORMAL)
        self.file_menu.AppendItem(self.save_mitem)

        self.saveas_mitem = wx.MenuItem(self.file_menu, wx.ID_ANY,
                                        u"Save As" + u"\t" + u"Ctrl+Shift+S",
                                        wx.EmptyString, wx.ITEM_NORMAL)
        self.file_menu.AppendItem(self.saveas_mitem)

        self.file_menu.AppendSeparator()

        self.quit_mitem = wx.MenuItem(self.file_menu, wx.ID_ANY,
                                      u"Quit" + u"\t" + u"Ctrl+W",
                                      wx.EmptyString, wx.ITEM_NORMAL)
        self.file_menu.AppendItem(self.quit_mitem)

        self.menu_bar.Append(self.file_menu, u"&File")

        self.edit_menu = wx.Menu()
        self.bl_mitem = wx.MenuItem(self.edit_menu, wx.ID_ANY,
                                    u"Beamline" + u"\t" + u"Ctrl+Shift+B",
                                    wx.EmptyString, wx.ITEM_NORMAL)
        self.edit_menu.AppendItem(self.bl_mitem)

        self.menu_bar.Append(self.edit_menu, u"&Edit")

        self.view_menu = wx.Menu()
        self.lte_mitem = wx.MenuItem(self.view_menu, wx.ID_ANY,
                                     u"Lattice File" + u"\t" + u"Ctrl+Shift+L",
                                     wx.EmptyString, wx.ITEM_NORMAL)
        self.view_menu.AppendItem(self.lte_mitem)

        self.raw_mitem = wx.MenuItem(self.view_menu, wx.ID_ANY,
                                     u"Raw String" + u"\t" + u"Ctrl+Shift+R",
                                     wx.EmptyString, wx.ITEM_NORMAL)
        self.view_menu.AppendItem(self.raw_mitem)

        self.dict_mitem = wx.MenuItem(self.view_menu, wx.ID_ANY,
                                      u"Dictionary" + u"\t" + u"Ctrl+Shift+D",
                                      wx.EmptyString, wx.ITEM_NORMAL)
        self.view_menu.AppendItem(self.dict_mitem)

        self.view_menu.AppendSeparator()

        self.expand_mitem = wx.MenuItem(
            self.view_menu, wx.ID_ANY, u"Expand Tree" + u"\t" +
            u"Ctrl+Shift+X", wx.EmptyString, wx.ITEM_RADIO)
        self.view_menu.AppendItem(self.expand_mitem)
        self.expand_mitem.Check(True)

        self.collapse_mitem = wx.MenuItem(
            self.view_menu, wx.ID_ANY, u"Collpase Tree" + u"\t" +
            u"Ctrl+Shift+P", wx.EmptyString, wx.ITEM_RADIO)
        self.view_menu.AppendItem(self.collapse_mitem)

        self.pt_mitem = wx.MenuItem(
            self.view_menu, wx.ID_ANY, u"Show path as title" + u"\t" +
            u"Ctrl+Shift+T", wx.EmptyString, wx.ITEM_CHECK)
        self.view_menu.AppendItem(self.pt_mitem)

        self.menu_bar.Append(self.view_menu, u"&View")

        self.tools_menu = wx.Menu()
        self.draw_mitem = wx.MenuItem(
            self.tools_menu, wx.ID_ANY, u"Visualization" + u"\t" +
            u"Ctrl+Shift+V", wx.EmptyString, wx.ITEM_NORMAL)
        self.tools_menu.AppendItem(self.draw_mitem)

        self.menu_bar.Append(self.tools_menu, u"&Tools")

        self.help_menu = wx.Menu()
        self.guide_mitem = wx.MenuItem(self.help_menu, wx.ID_ANY,
                                       u"Guide" + u"\t" + u"F1",
                                       wx.EmptyString, wx.ITEM_NORMAL)
        self.help_menu.AppendItem(self.guide_mitem)

        self.about_mitem = wx.MenuItem(self.help_menu, wx.ID_ABOUT,
                                       u"About" + u"\t" + u"Ctrl+A",
                                       wx.EmptyString, wx.ITEM_NORMAL)
        self.help_menu.AppendItem(self.about_mitem)

        self.menu_bar.Append(self.help_menu, u"&Help")

        self.SetMenuBar(self.menu_bar)

        self.Centre(wx.BOTH)

        # Connect Events
        self.treename_tc.Bind(wx.EVT_TEXT_ENTER, self.treename_tcOnTextEnter)
        self.show_btn.Bind(wx.EVT_BUTTON, self.show_btnOnButtonClick)
        self.generate_btn.Bind(wx.EVT_BUTTON, self.generate_btnOnButtonClick)
        self.model_btn.Bind(wx.EVT_BUTTON, self.model_btnOnButtonClick)
        self.clear_btn.Bind(wx.EVT_BUTTON, self.clear_btnOnButtonClick)
        self.exit_btn.Bind(wx.EVT_BUTTON, self.exit_btnOnButtonClick)
        self.mainview_tree.Bind(wx.EVT_LEFT_DOWN, self.mainview_treeOnLeftDown)
        self.nodeview_lc.Bind(wx.EVT_LIST_COL_RIGHT_CLICK,
                              self.nodeview_lcOnListColRightClick)
        self.nodeview_lc.Bind(wx.EVT_LIST_ITEM_SELECTED,
                              self.nodeview_lcOnListItemSelected)
        self.nodeview_lc.Bind(wx.EVT_RIGHT_UP, self.nodeview_lcOnRightUp)
        self.search_ctrl.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN,
                              self.search_ctrlOnCancelButton)
        self.search_ctrl.Bind(wx.EVT_TEXT, self.search_ctrlOnText)
        self.search_ctrl.Bind(wx.EVT_TEXT_ENTER, self.search_ctrlOnTextEnter)
        self.next_bmpbtn.Bind(wx.EVT_BUTTON, self.next_bmpbtnOnButtonClick)
        self.previous_bmpbtn.Bind(wx.EVT_BUTTON,
                                  self.previous_bmpbtnOnButtonClick)
        self.showlog_btn.Bind(wx.EVT_BUTTON, self.showlog_btnOnButtonClick)
        self.Bind(wx.EVT_MENU,
                  self.open_mitemOnMenuSelection,
                  id=self.open_mitem.GetId())
        self.Bind(wx.EVT_MENU,
                  self.reopen_mitemOnMenuSelection,
                  id=self.reopen_mitem.GetId())
        self.Bind(wx.EVT_MENU,
                  self.save_mitemOnMenuSelection,
                  id=self.save_mitem.GetId())
        self.Bind(wx.EVT_MENU,
                  self.saveas_mitemOnMenuSelection,
                  id=self.saveas_mitem.GetId())
        self.Bind(wx.EVT_MENU,
                  self.quit_mitemOnMenuSelection,
                  id=self.quit_mitem.GetId())
        self.Bind(wx.EVT_MENU,
                  self.bl_mitemOnMenuSelection,
                  id=self.bl_mitem.GetId())
        self.Bind(wx.EVT_MENU,
                  self.lte_mitemOnMenuSelection,
                  id=self.lte_mitem.GetId())
        self.Bind(wx.EVT_MENU,
                  self.raw_mitemOnMenuSelection,
                  id=self.raw_mitem.GetId())
        self.Bind(wx.EVT_MENU,
                  self.dict_mitemOnMenuSelection,
                  id=self.dict_mitem.GetId())
        self.Bind(wx.EVT_MENU,
                  self.expand_mitemOnMenuSelection,
                  id=self.expand_mitem.GetId())
        self.Bind(wx.EVT_MENU,
                  self.collapse_mitemOnMenuSelection,
                  id=self.collapse_mitem.GetId())
        self.Bind(wx.EVT_MENU,
                  self.pt_mitemOnMenuSelection,
                  id=self.pt_mitem.GetId())
        self.Bind(wx.EVT_MENU,
                  self.draw_mitemOnMenuSelection,
                  id=self.draw_mitem.GetId())
        self.Bind(wx.EVT_MENU,
                  self.guide_mitemOnMenuSelection,
                  id=self.guide_mitem.GetId())
        self.Bind(wx.EVT_MENU,
                  self.about_mitemOnMenuSelection,
                  id=self.about_mitem.GetId())

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def treename_tcOnTextEnter(self, event):
        event.Skip()

    def show_btnOnButtonClick(self, event):
        event.Skip()

    def generate_btnOnButtonClick(self, event):
        event.Skip()

    def model_btnOnButtonClick(self, event):
        event.Skip()

    def clear_btnOnButtonClick(self, event):
        event.Skip()

    def exit_btnOnButtonClick(self, event):
        event.Skip()

    def mainview_treeOnLeftDown(self, event):
        event.Skip()

    def nodeview_lcOnListColRightClick(self, event):
        event.Skip()

    def nodeview_lcOnListItemSelected(self, event):
        event.Skip()

    def nodeview_lcOnRightUp(self, event):
        event.Skip()

    def search_ctrlOnCancelButton(self, event):
        event.Skip()

    def search_ctrlOnText(self, event):
        event.Skip()

    def search_ctrlOnTextEnter(self, event):
        event.Skip()

    def next_bmpbtnOnButtonClick(self, event):
        event.Skip()

    def previous_bmpbtnOnButtonClick(self, event):
        event.Skip()

    def showlog_btnOnButtonClick(self, event):
        event.Skip()

    def open_mitemOnMenuSelection(self, event):
        event.Skip()

    def reopen_mitemOnMenuSelection(self, event):
        event.Skip()

    def save_mitemOnMenuSelection(self, event):
        event.Skip()

    def saveas_mitemOnMenuSelection(self, event):
        event.Skip()

    def quit_mitemOnMenuSelection(self, event):
        event.Skip()

    def bl_mitemOnMenuSelection(self, event):
        event.Skip()

    def lte_mitemOnMenuSelection(self, event):
        event.Skip()

    def raw_mitemOnMenuSelection(self, event):
        event.Skip()

    def dict_mitemOnMenuSelection(self, event):
        event.Skip()

    def expand_mitemOnMenuSelection(self, event):
        event.Skip()

    def collapse_mitemOnMenuSelection(self, event):
        event.Skip()

    def pt_mitemOnMenuSelection(self, event):
        event.Skip()

    def draw_mitemOnMenuSelection(self, event):
        event.Skip()

    def guide_mitemOnMenuSelection(self, event):
        event.Skip()

    def about_mitemOnMenuSelection(self, event):
        event.Skip()

    def tree_splitterOnIdle(self, event):
        self.tree_splitter.SetSashPosition(0)
        self.tree_splitter.Unbind(wx.EVT_IDLE)

    ###########################################################################
    ## Class DrawFrame
    ###########################################################################


class DrawFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self,
                          parent,
                          id=wx.ID_ANY,
                          title=wx.EmptyString,
                          pos=wx.DefaultPosition,
                          size=wx.Size(800, 600),
                          style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        main_vbox = wx.BoxSizer(wx.VERTICAL)

        info_svbox = wx.StaticBoxSizer(
            wx.StaticBox(self, wx.ID_ANY,
                         u"Visualization Options"), wx.VERTICAL)

        self.m_panel = wx.Panel(info_svbox.GetStaticBox(), wx.ID_ANY,
                                wx.DefaultPosition, wx.DefaultSize,
                                wx.TAB_TRAVERSAL)
        vbox_top = wx.BoxSizer(wx.VERTICAL)

        hbox_top = wx.BoxSizer(wx.HORIZONTAL)

        self.bl_info_st_name = wx.StaticText(
            self.m_panel, wx.ID_ANY, u"Selected Beamline:", wx.DefaultPosition,
            wx.DefaultSize, wx.ALIGN_LEFT)
        self.bl_info_st_name.Wrap(-1)
        hbox_top.Add(self.bl_info_st_name, 0, wx.ALL, 5)

        self.bl_info_st_val = wx.StaticText(self.m_panel, wx.ID_ANY,
                                            wx.EmptyString, wx.DefaultPosition,
                                            wx.DefaultSize, wx.ALIGN_LEFT)
        self.bl_info_st_val.Wrap(-1)
        self.bl_info_st_val.SetForegroundColour(wx.Colour(0, 0, 255))

        hbox_top.Add(self.bl_info_st_val, 0, wx.ALL, 5)

        vbox_top.Add(hbox_top, 1, wx.EXPAND, 5)

        hbox_bottom = wx.BoxSizer(wx.HORIZONTAL)

        mode_rbChoices = [u"plain", u"fancy"]
        self.mode_rb = wx.RadioBox(self.m_panel, wx.ID_ANY, u"Mode",
                                   wx.DefaultPosition, wx.DefaultSize,
                                   mode_rbChoices, 1, wx.RA_SPECIFY_COLS)
        self.mode_rb.SetSelection(1)
        hbox_bottom.Add(self.mode_rb, 1, wx.BOTTOM | wx.LEFT | wx.RIGHT, 5)

        annote_sb = wx.StaticBoxSizer(
            wx.StaticBox(self.m_panel, wx.ID_ANY,
                         u"Tag Options"), wx.HORIZONTAL)

        self.quad_ckb = wx.CheckBox(annote_sb.GetStaticBox(), wx.ID_ANY,
                                    u"Quad", wx.DefaultPosition,
                                    wx.DefaultSize, 0)
        annote_sb.Add(self.quad_ckb, 0, wx.ALL, 5)

        self.bend_ckb = wx.CheckBox(annote_sb.GetStaticBox(), wx.ID_ANY,
                                    u"Bend", wx.DefaultPosition,
                                    wx.DefaultSize, 0)
        annote_sb.Add(self.bend_ckb, 0, wx.ALL, 5)

        self.rf_ckb = wx.CheckBox(annote_sb.GetStaticBox(), wx.ID_ANY, u"RF",
                                  wx.DefaultPosition, wx.DefaultSize, 0)
        annote_sb.Add(self.rf_ckb, 0, wx.ALL, 5)

        self.monitor_ckb = wx.CheckBox(annote_sb.GetStaticBox(), wx.ID_ANY,
                                       u"Monitor", wx.DefaultPosition,
                                       wx.DefaultSize, 0)
        annote_sb.Add(self.monitor_ckb, 0, wx.ALL, 5)

        self.undulator_ckb = wx.CheckBox(annote_sb.GetStaticBox(), wx.ID_ANY,
                                         u"Undulator", wx.DefaultPosition,
                                         wx.DefaultSize, 0)
        annote_sb.Add(self.undulator_ckb, 0, wx.ALL, 5)

        hbox_bottom.Add(annote_sb, 2, wx.ALIGN_TOP | wx.BOTTOM | wx.EXPAND |
                        wx.LEFT, 5)

        vbox_top.Add(hbox_bottom, 0, wx.EXPAND, 5)

        self.m_panel.SetSizer(vbox_top)
        self.m_panel.Layout()
        vbox_top.Fit(self.m_panel)
        info_svbox.Add(self.m_panel, 0, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND,
                       5)

        main_vbox.Add(info_svbox, 0, wx.ALL | wx.EXPAND, 10)

        draw_svbox = wx.StaticBoxSizer(
            wx.StaticBox(self, wx.ID_ANY, u"Drawing"), wx.VERTICAL)

        draw_vbox = wx.BoxSizer(wx.VERTICAL)

        self.drawing_panel = pltutils.LatticePlotPanel(
            self, dpi=75, toolbar=True,
            type='image')
        draw_vbox.Add(self.drawing_panel, 1, wx.EXPAND, 0)

        draw_svbox.Add(draw_vbox, 1, wx.EXPAND, 5)

        main_vbox.Add(draw_svbox, 1, wx.BOTTOM | wx.EXPAND | wx.LEFT |
                      wx.RIGHT, 10)

        self.SetSizer(main_vbox)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.mode_rb.Bind(wx.EVT_RADIOBOX, self.mode_rbOnRadioBox)
        self.quad_ckb.Bind(wx.EVT_CHECKBOX, self.quad_ckbOnCheckBox)
        self.bend_ckb.Bind(wx.EVT_CHECKBOX, self.bend_ckbOnCheckBox)
        self.rf_ckb.Bind(wx.EVT_CHECKBOX, self.rf_ckbOnCheckBox)
        self.monitor_ckb.Bind(wx.EVT_CHECKBOX, self.monitor_ckbOnCheckBox)
        self.undulator_ckb.Bind(wx.EVT_CHECKBOX, self.undulator_ckbOnCheckBox)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def mode_rbOnRadioBox(self, event):
        event.Skip()

    def quad_ckbOnCheckBox(self, event):
        event.Skip()

    def bend_ckbOnCheckBox(self, event):
        event.Skip()

    def rf_ckbOnCheckBox(self, event):
        event.Skip()

    def monitor_ckbOnCheckBox(self, event):
        event.Skip()

    def undulator_ckbOnCheckBox(self, event):
        event.Skip()

    ###########################################################################
    ## Class BeamlineFrame
    ###########################################################################


class BeamlineFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self,
                          parent,
                          id=wx.ID_ANY,
                          title=wx.EmptyString,
                          pos=wx.DefaultPosition,
                          size=wx.Size(700, 500),
                          style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        choice_vbox = wx.BoxSizer(wx.VERTICAL)

        self.bl_choicebook = wx.Choicebook(self, wx.ID_ANY, wx.DefaultPosition,
                                           wx.DefaultSize, wx.CHB_DEFAULT)
        choice_vbox.Add(self.bl_choicebook, 1, wx.EXPAND, 0)

        ctrl_hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.ok_btn = wx.Button(self, wx.ID_ANY, u"&OK", wx.DefaultPosition,
                                wx.DefaultSize, 0)
        ctrl_hbox.Add(self.ok_btn, 0, wx.ALL, 5)

        self.cancel_btn = wx.Button(self, wx.ID_ANY, u"&Cancel",
                                    wx.DefaultPosition, wx.DefaultSize, 0)
        ctrl_hbox.Add(self.cancel_btn, 0, wx.ALL, 5)

        choice_vbox.Add(ctrl_hbox, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.SetSizer(choice_vbox)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.bl_choicebook.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGED,
                                self.bl_choicebookOnChoicebookPageChanged)
        self.ok_btn.Bind(wx.EVT_BUTTON, self.ok_btnOnButtonClick)
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.cancel_btnOnButtonClick)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def bl_choicebookOnChoicebookPageChanged(self, event):
        event.Skip()

    def ok_btnOnButtonClick(self, event):
        event.Skip()

    def cancel_btnOnButtonClick(self, event):
        event.Skip()

    ###########################################################################
    ## Class LogFrame
    ###########################################################################


class LogFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self,
                          parent,
                          id=wx.ID_ANY,
                          title=wx.EmptyString,
                          pos=wx.DefaultPosition,
                          size=wx.Size(800, 600),
                          style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        main_vbox = wx.BoxSizer(wx.VERTICAL)

        self.log_tc = wx.TextCtrl(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
            wx.DefaultSize, wx.HSCROLL | wx.TE_MULTILINE | wx.TE_READONLY)
        self.log_tc.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), 70, 90, 90,
                                    False, "Monospace"))
        self.log_tc.SetForegroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOWTEXT))
        self.log_tc.SetBackgroundColour(wx.Colour(240, 240, 240))

        main_vbox.Add(self.log_tc, 1, wx.ALL | wx.EXPAND, 10)

        control_hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.copy_btn = wx.Button(self, wx.ID_ANY, u"&Copy",
                                  wx.DefaultPosition, wx.DefaultSize, 0)
        control_hbox.Add(self.copy_btn, 0, wx.ALIGN_BOTTOM | wx.LEFT, 10)

        self.exit_btn = wx.Button(self, wx.ID_ANY, u"E&xit",
                                  wx.DefaultPosition, wx.DefaultSize, 0)
        control_hbox.Add(self.exit_btn, 0, wx.ALIGN_CENTER | wx.LEFT |
                         wx.RIGHT, 10)

        main_vbox.Add(control_hbox, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        self.SetSizer(main_vbox)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.copy_btn.Bind(wx.EVT_BUTTON, self.copy_btnOnButtonClick)
        self.exit_btn.Bind(wx.EVT_BUTTON, self.exit_btnOnButtonClick)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def copy_btnOnButtonClick(self, event):
        event.Skip()

    def exit_btnOnButtonClick(self, event):
        event.Skip()

    ###########################################################################
    ## Class DataFrame
    ###########################################################################


class DataFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self,
                          parent,
                          id=wx.ID_ANY,
                          title=wx.EmptyString,
                          pos=wx.DefaultPosition,
                          size=wx.Size(950, 700),
                          style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        main_vbox = wx.BoxSizer(wx.VERTICAL)

        self.data_rtc = wx.richtext.RichTextCtrl(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
            wx.DefaultSize, wx.TE_READONLY | wx.VSCROLL | wx.HSCROLL |
            wx.NO_BORDER | wx.WANTS_CHARS)
        self.data_rtc.SetFont(wx.Font(12, 76, 90, 90, False, "Monospace"))

        main_vbox.Add(self.data_rtc, 1, wx.EXPAND | wx.ALL, 5)

        control_hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.copy_btn = wx.Button(self, wx.ID_ANY, u"&Copy",
                                  wx.DefaultPosition, wx.DefaultSize, 0)
        control_hbox.Add(self.copy_btn, 0, wx.ALIGN_BOTTOM | wx.LEFT, 10)

        self.exit_btn = wx.Button(self, wx.ID_ANY, u"E&xit",
                                  wx.DefaultPosition, wx.DefaultSize, 0)
        control_hbox.Add(self.exit_btn, 0, wx.ALIGN_CENTER | wx.LEFT |
                         wx.RIGHT, 10)

        main_vbox.Add(control_hbox, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        self.SetSizer(main_vbox)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.copy_btn.Bind(wx.EVT_BUTTON, self.copy_btnOnButtonClick)
        self.exit_btn.Bind(wx.EVT_BUTTON, self.exit_btnOnButtonClick)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def copy_btnOnButtonClick(self, event):
        event.Skip()

    def exit_btnOnButtonClick(self, event):
        event.Skip()
