from pyHook import HookManager
import wx

from tooltips import tooltip_x, tooltip_y, tooltip_record_coord, \
    tooltip_delete_coord


class CoordHandler:
    def _add_motionctrl_headline(self):
        '''Convenience function for adding label headline to the coordinate list'''
        # Creating widgets
        lbl_empty = lambda: wx.StaticText(self.coords_settings, label="")
        lbl_x = wx.StaticText(self.coords_settings, label="X")
        lbl_y = wx.StaticText(self.coords_settings, label="Y")
        
        # Changing font
        font = lbl_x.GetFont()
        font.SetWeight(wx.BOLD)
        lbl_x.SetFont(font)
        lbl_y.SetFont(font)
        
        # Adding widgets to sizer
        self.motionctrl.AddMany([lbl_empty(), (lbl_x, 0, wx.ALIGN_CENTER), (lbl_y, 0, wx.ALIGN_CENTER), lbl_empty(), lbl_empty()])
    
    
    def add_coords(self, event):
        '''Add coordinate widgets (X and Y spinners + record button)'''
        count_rows = self.motionctrl.GetEffectiveRowsCount()
        
        # Creating settings widgets
        number = wx.StaticText(self.coords_settings, label=str(count_rows) + ")")
        move_x = wx.SpinCtrl(self.coords_settings, size=(60, -1),
                             min=-self.screen_dimensions[0], max=self.screen_dimensions[0])
        move_y = wx.SpinCtrl(self.coords_settings, size=(60, -1),
                             min=-self.screen_dimensions[1], max=self.screen_dimensions[1])
        record = wx.Button(self.coords_settings, label="Record", size=(60, -1))
        delete = wx.Button(self.coords_settings, size=(26, -1))
        
        delete.SetBitmap(wx.Bitmap("icons/delete.png"))
        
        # Adding widgets to sizers
        self.motionctrl.AddMany([(number, 0, wx.ALIGN_CENTER_VERTICAL), move_x, move_y, record, delete])
        
        # Adding tooltips
        move_x.SetToolTipString(tooltip_x)
        move_y.SetToolTipString(tooltip_y)
        record.SetToolTipString(tooltip_record_coord)
        delete.SetToolTipString(tooltip_delete_coord)
        
        # Make number bold
        font = number.GetFont()
        font.SetWeight(wx.BOLD)
        number.SetFont(font)
        
        # Binding events
        move_x.Bind(wx.EVT_KILL_FOCUS, self.save_profile)
        move_y.Bind(wx.EVT_KILL_FOCUS, self.save_profile)
        self.Bind(wx.EVT_BUTTON, self.init_record, record)
        self.Bind(wx.EVT_BUTTON, self.delete_coords, delete)
        
        # Update scrolled window
        self.coords_settings.Layout()
        old_size = self.coords_settings.GetSizer().GetSize()
        new_size = (old_size[0] + 1, old_size[1])
        self.coords_settings.SetVirtualSize(new_size)
        self.coords_settings.Scroll(0, self.coords_settings.GetScrollRange(wx.VERTICAL))
        
        # Add input widgets to list (to be used by main loop later)
        self.coordinates.append([move_x, move_y])
        
        if event != None:
            self.save_profile(None)
    
    
    def delete_coords(self, event):
        '''Function for deleting an already existing coordinate'''
        if self.motionctrl.GetEffectiveRowsCount() > 2:
            obj = event.GetEventObject()
            
            # Collecting all widgets to be deleted
            delete_widgets = [wx.FindWindowById(obj.GetId() - i) for i in range(self.motionctrl.GetCols())]
            
            # Updating coordinate numbers
            all_ids = sorted([child.GetWindow().GetId() for child in self.motionctrl.GetChildren()])
            for x in all_ids[all_ids.index(delete_widgets[-1].GetId())::5][1:]:
                widget = wx.FindWindowById(x)
                widget.SetLabel(str(int(widget.GetLabel()[0]) - 1) + ")")
            
            # Removing coordinate from list
            self.coordinates.pop(int(delete_widgets[-1].GetLabel()[0]) - 1)
            
            # Destroying all widgets related to the deleted coordinate
            for widget in delete_widgets:
                widget.Destroy()
            self.motionctrl.Layout()
            
            # Saving settings
            self.save_profile(None)
    
    
    def clear_coords(self, event):
        '''Function for resetting all coordinates'''
        for coords in self.coordinates:
            for widget in coords:
                widget.SetValue(0)
        
        self.save_profile(None)
    
    
    def init_record(self, event):
        '''Initiate recording of cursor positions'''
        # Preparing variables
        obj = event.GetEventObject()
        self.coord_counter = 0
        self.coord_widgets = []
        if self.movement_relative:
            self.last_coord = None
        
        # Starting listening for mouse presses
        if not hasattr(self, "hook"):
            self.hook = HookManager()
        self.hook.HookMouse()
        
        # Indicating recording
        self.frame.statusbar.SetStatusText("Recording cursor positions...")
        self.frame.SetTitle("MouseMove - Recording positions")
        if obj in [self.record, self.frame.page_keyconfig]: # Need the keyconfig reference to make hotkey work
            first_coord = self.motionctrl.GetChildren()[5].GetWindow()
            self.hook.MouseLeftDown = self.record_coords
        else:
            first_coord = wx.FindWindowById(obj.GetId() - 3)
            self.first_coord = first_coord
            self.hook.MouseLeftDown = self.record_single_coord
        first_coord.SetForegroundColour("Red")
        first_coord.Refresh()
    
    
    def stop_record(self):
        '''Actions to be performed when stopping recording'''
        self.hook.UnhookMouse()
        self.frame.statusbar.SetStatusText("")
        self.frame.SetTitle("MouseMove")
        
        self.save_profile(None)
