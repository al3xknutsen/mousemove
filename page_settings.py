from ctypes import windll
from os import listdir
from os.path import getsize

import wx

from coords import CoordHandler
from record import RecordHandler
from save_load import SaveLoad_Profiles
from tooltips import tooltip_add, tooltip_auto_stop, tooltip_clear, \
    tooltip_hold_mouse, tooltip_interval, tooltip_movement_absolute, \
    tooltip_movement_relative, tooltip_record


class Settings(wx.Panel, CoordHandler, RecordHandler, SaveLoad_Profiles):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        self.frame = wx.GetTopLevelParent(self)
        self.coordinates = []
        self.screen_dimensions = [windll.user32.GetSystemMetrics(x) for x in [0, 1]]
        
        # Creating sizers
        box = wx.BoxSizer()
        grid = wx.FlexGridSizer(1, 0, 20, 20)
        main_settings = wx.FlexGridSizer(0, 1, 15, 15)
        movement_settings = wx.FlexGridSizer(0, 1, 10, 10)
        movement_type = wx.GridSizer(1, 2, 5, 5)
        buttons = wx.GridSizer(1, 2, 5, 5)
        sizer_interval = wx.FlexGridSizer(0, 2, 10, 10)
        
        # Creating boxes
        box_general_settings = wx.StaticBox(self, label="General settings")
        box_movement = wx.StaticBox(self, label="Movement")
        sizer_general_settings = wx.StaticBoxSizer(box_general_settings)
        sizer_movement = wx.StaticBoxSizer(box_movement)
        
        
        ## ------- CREATING SCROLLED WINDOW ------- ##
        self.coords_settings = wx.ScrolledWindow(box_movement, size=(280, 100))
        
        # Creating sizers
        coords_box = wx.BoxSizer()
        self.motionctrl = wx.FlexGridSizer(0, 5, 10, 10)
        
        # Adding widgets to sizers
        coords_box.Add(self.motionctrl, 0, wx.ALL, 0)
        self.coords_settings.SetSizer(coords_box)
        
        # Setting scrollbar
        self.coords_settings.SetScrollRate(5, 5)
        ## ---------------------------------------- ##
        
        
        # Creating settings widgets
        self.movement_absolute = wx.RadioButton(box_movement, label="Absolute")
        self.movement_relative = wx.RadioButton(box_movement, label="Relative")
        add = wx.Button(box_movement, label="Add coordinates")
        clear = wx.Button(box_movement, label="Clear")
        self.record = wx.Button(box_movement, label="Record positions")
        lbl_interval = wx.StaticText(box_general_settings, label="Move interval (ms):")
        self.interval = wx.SpinCtrl(box_general_settings, size=(80, -1), min=10, max=1000000, initial=100)
        self.hold_mouse = wx.CheckBox(box_general_settings, label="Hold mouse button")
        self.auto_stop = wx.CheckBox(box_general_settings, label="Stop when moving mouse manually")
        
        # Adding widgets to sizers
        sizer_interval.AddMany([(lbl_interval, 0, wx.ALIGN_CENTER_VERTICAL), self.interval])
        main_settings.AddMany([sizer_interval, self.hold_mouse, self.auto_stop])
        movement_type.AddMany([self.movement_absolute, self.movement_relative])
        buttons.AddMany([(add, 0, wx.EXPAND), (clear, 0, wx.EXPAND)])
        movement_settings.AddMany([(movement_type, 0, wx.ALIGN_CENTER), (wx.StaticLine(box_movement), 0, wx.EXPAND),
                                   (self.coords_settings, 0, wx.EXPAND), (wx.StaticLine(box_movement), 0, wx.EXPAND),
                                   (buttons, 0, wx.EXPAND), (self.record, 0, wx.EXPAND)])
        grid.AddMany([sizer_movement, sizer_general_settings])
        box.Add(grid, 0, wx.ALL, 20)
        self.SetSizer(box)
        
        # Adding content to boxes
        sizer_general_settings.Add(main_settings, 0, wx.ALL, 10)
        sizer_movement.Add(movement_settings, 0, wx.ALL, 10)
        
        # Changing fonts
        font = box_general_settings.GetFont()
        font.SetPointSize(12)
        font.SetStyle(wx.ITALIC)
        box_general_settings.SetFont(font)
        box_movement.SetFont(font)
        
        font = add.GetFont()
        font.SetWeight(wx.BOLD)
        add.SetFont(font)
        
        # Adding tooltips
        self.movement_absolute.SetToolTipString(tooltip_movement_absolute)
        self.movement_relative.SetToolTipString(tooltip_movement_relative)
        add.SetToolTipString(tooltip_add)
        clear.SetToolTipString(tooltip_clear)
        self.record.SetToolTipString(tooltip_record)
        lbl_interval.SetToolTipString(tooltip_interval)
        self.interval.SetToolTipString(tooltip_interval)
        self.hold_mouse.SetToolTipString(tooltip_hold_mouse)
        self.auto_stop.SetToolTipString(tooltip_auto_stop)
        
        # Loading settings
        SaveLoad_Profiles.__init__(self)
        if "Default.txt" not in listdir(self.path_profiles) or getsize(self.path_profiles + "Default.txt") == 0:
            self.add_coords(None)
            self.save_profile(None)
            self.coordinates = []
        self.load_profile()
        
        # Binding events
        self.Bind(wx.EVT_RADIOBUTTON, self.change_movement_absolute, self.movement_absolute)
        self.Bind(wx.EVT_RADIOBUTTON, self.change_movement_relative, self.movement_relative)
        self.Bind(wx.EVT_BUTTON, self.add_coords, add)
        self.Bind(wx.EVT_BUTTON, self.clear_coords, clear)
        self.Bind(wx.EVT_BUTTON, self.init_record, self.record)
        
        self.Bind(wx.EVT_RADIOBUTTON, self.save_profile, self.movement_absolute)
        self.Bind(wx.EVT_RADIOBUTTON, self.save_profile, self.movement_relative)
        self.interval.Bind(wx.EVT_KILL_FOCUS, self.save_profile)
        self.Bind(wx.EVT_CHECKBOX, self.save_profile, self.hold_mouse)
        self.Bind(wx.EVT_CHECKBOX, self.save_profile, self.auto_stop)
    
    
    def change_movement_absolute(self, event):
        '''When movement is absolute: change minimum coordinates to 0'''
        for widget in [w for coords in self.coordinates for w in coords]:
            widget.SetRange(0, widget.GetMax())
    
    
    def change_movement_relative(self, event):
        '''When movement is relative: change minimum coordinates to negative screen size'''
        for i in [0, 1]:
            for widget in [coords[i] for coords in self.coordinates]:
                widget.SetRange(-self.screen_dimensions[i], widget.GetMax())
    