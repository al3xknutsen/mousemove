from win32api import GetCursorPos
import wx


class RecordHandler:
    def record_coords(self, event):
        '''Record mouse position at mouse press, and input coordinates into widgets'''
        cursorpos = GetCursorPos()
        
        if self.movement_relative.GetValue():
            # Set initial cursor position
            if not self.last_coord:
                self.coord_counter -= 1 # Negate the += 1 (this coordinate is origin, not position)
            else:
                # Set new point (all further positions derive from this)
                self._fill_coords([cursorpos[i] - self.last_coord[i] for i in [0, 1]])
            self.last_coord = cursorpos
        
        else:
            self._fill_coords(cursorpos)
        
        self.coord_counter += 1
        
        # Quit if all widgets have been filled
        if self.coord_counter == self.motionctrl.GetEffectiveRowsCount() - 1:
            self.stop_record()
        
        return True # Needed for the hook manager
    
    
    def record_single_coord(self, event):
        '''Function for recording a single coordinate'''
        num_id = self.first_coord.GetId()
        x = wx.FindWindowById(num_id + 1)
        y = wx.FindWindowById(num_id + 2)
        
        cursorpos = GetCursorPos()
        
        def stop_record():
            '''Sub-function for resetting label color and stopping recording'''
            self.first_coord.SetForegroundColour("black")
            self.first_coord.Refresh()
            self.stop_record()
        
        if self.movement_relative.GetValue():
            # Set origin point for relative coordinates
            if not self.last_coord:
                self.last_coord = cursorpos
            else:
                # Input coordinates in list (relative to origin point)
                for i, widget in enumerate([x, y]):
                    widget.SetValue(cursorpos[i] - self.last_coord[i])
                stop_record()
        else:
            # Input cursor position in list (absolute coordinates)
            for i, widget in enumerate([x, y]):
                widget.SetValue(cursorpos[i])
            stop_record()
        
        return True
    
    
    def _fill_coords(self, coords):
        '''Function for filling values into widgets'''
        
        columns = self.motionctrl.GetCols()
        
        # Filling values into widgets
        for i, widget in enumerate(self.coordinates[self.coord_counter]):
            widget.SetValue(coords[i])
        
        widgets = self.motionctrl.GetChildren()
        
        # Reverting color back to black
        current_num = widgets[self.coord_counter * columns + columns].GetWindow()
        current_num.SetForegroundColour("black")
        current_num.Refresh()
        
        # Indicating which position is awaiting input
        if self.coord_counter < len(self.coordinates) - 1:
            next_num = widgets[self.coord_counter * columns + columns * 2].GetWindow()
            next_num.SetForegroundColour("red")
            next_num.Refresh()