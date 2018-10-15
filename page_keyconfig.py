import wx

from save_load import SaveLoad_Keyconfig
from TRANSLATION_TABLES import TABLE_KEYS, TABLE_MODIFIERS


class KeyConfig(wx.Panel, SaveLoad_Keyconfig):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        # Preparing container variables, for easier access
        self.modifiers = []
        self.keys = []
        labels = []
        
        # Get topmost frame
        self.frame = wx.GetTopLevelParent(self)
        
        # Creating sizers
        box = wx.BoxSizer()
        grid = wx.FlexGridSizer(0, 1, 20, 20)
        keymap = wx.FlexGridSizer(0, 3, 10, 20)
        
        # Creating labels and widgets
        style_keyinput = wx.TE_PROCESS_ENTER | wx.TE_PROCESS_TAB | wx.TE_CENTER
        lbl_empty = wx.StaticText(self, label="")
        lbl_modifier = wx.StaticText(self, label="Modifiers")
        lbl_key = wx.StaticText(self, label="Key")
        
        for hotkey_name in ["start", "stop", "record", "change profile", "toggle mouse hold"]:
            labels.append(wx.StaticText(self, label=hotkey_name.upper()))
        
        clear = wx.Button(self, label="Clear")
        
        def add_modifiers():
            '''Function for adding modifier widgets (Ctrl, Shift & Alt)'''
            modifiers = wx.FlexGridSizer(1, 3, 5, 5)
            mod_ctrl = wx.CheckBox(self, label="Ctrl")
            mod_shift = wx.CheckBox(self, label="Shift")
            mod_alt = wx.CheckBox(self, label="Alt")
            modifiers.AddMany([mod_ctrl, mod_shift, mod_alt])
            
            # Adding widgets to list, for easier access
            self.modifiers.extend([mod_ctrl, mod_shift, mod_alt])
            
            return modifiers
        
        # Adding widgets to sizers
        keymap.AddMany([lbl_empty, (lbl_modifier, 0, wx.ALIGN_CENTER), (lbl_key, 0, wx.ALIGN_CENTER)])
        # Adding main widgets (modifier and key inputs)
        for label in labels:
            key_input = wx.TextCtrl(self, style=style_keyinput)
            self.keys.append(key_input)
            keymap.AddMany([(label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT), (add_modifiers(), 0, wx.ALIGN_CENTER_VERTICAL),
                            key_input])
        
        grid.AddMany([keymap, (clear, 0, wx.ALIGN_CENTER)])
        box.AddStretchSpacer()
        box.Add(grid, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 20)
        box.AddStretchSpacer()
        self.SetSizer(box)
        
        # Changing fonts
        font = labels[0].GetFont()
        font.SetWeight(wx.BOLD)
        font.SetPointSize(10)
        for widget in [lbl_modifier, lbl_key]:
            widget.SetFont(font)
        font.SetStyle(wx.ITALIC)
        for label in labels:
            label.SetFont(font)
        
        # Grouping modifier widgets, for easier access
        _indexes = range(0, len(self.modifiers) + 1, 3)
        self.modifier_groups = [self.modifiers[i:j] for i, j in zip(_indexes[:-1], _indexes[1:])]
        
        # Binding events
        for modifier in self.modifiers:
            self.Bind(wx.EVT_CHECKBOX, self.register_hotkeys, modifier)
        for key in self.keys:
            key.Bind(wx.EVT_KEY_DOWN, self.assign_key)
        self.Bind(wx.EVT_BUTTON, self.clear_hotkeys, clear)
        
        # Loading keyconfig from file
        SaveLoad_Keyconfig.__init__(self)
        self.load_keyconfig()

    
    def assign_key(self, event):
        '''Creating global hotkey based on user input'''
        obj = event.GetEventObject()
        keycode = event.GetRawKeyCode()
        
        # Translate raw key code into human-readable text
        CODE_TO_TEXT = dict(zip(TABLE_KEYS.values(), TABLE_KEYS.keys()))
        if keycode in CODE_TO_TEXT:
            obj.SetValue(CODE_TO_TEXT[keycode])
        else:
            obj.SetValue(str(keycode))
        
        self.register_hotkeys(None)
        self.save_keyconfig()
    
    
    def register_hotkeys(self, event):
        '''Function for fetching input values and registering hotkeys based on said values'''
        
        # Collecting values and applying hotkeys
        for i, modifiers, key in zip(range(1, len(self.keys) + 1), self.modifier_groups, self.keys):
            k = key.GetValue()
            mod_value = sum([TABLE_MODIFIERS[widget.GetLabel().upper()] for widget in modifiers if widget.GetValue()])
            key_value = TABLE_KEYS[k] if k in TABLE_KEYS else (int(k)) if len(k) > 0 else 0
            
            self.RegisterHotKey(i, mod_value, key_value)
        
        # Binding functions to hotkeys
        self.Bind(wx.EVT_HOTKEY, self.frame.thread_move_loop, id=1)
        self.Bind(wx.EVT_HOTKEY, self.frame.stop_motion, id=2)
        self.Bind(wx.EVT_HOTKEY, self.frame.page_settings.init_record, id=3)
        self.Bind(wx.EVT_HOTKEY, self.frame.next_profile, id=4)
        self.Bind(wx.EVT_HOTKEY, self.frame.toggle_mouse, id=5)
        
        # Saving keyconfig to file
        if event != None:
            self.save_keyconfig()
    
    
    def unregister_hotkeys(self):
        '''Function for erasing all previously registered hotkeys'''
        for i in range(1, len(self.keys) + 1):
            self.UnregisterHotKey(i)
    
    
    def clear_hotkeys(self, event):
        '''Function for clearing all hotkey inputs'''
        
        # Clearing all inputs
        for modifier in self.modifiers:
            modifier.SetValue(False)
        for key in self.keys:
            key.Clear()
        
        # Clearing hotkeys
        self.unregister_hotkeys()
        
        # Saving keymap
        self.save_keyconfig()
