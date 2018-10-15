from ctypes import windll
from os import getenv, listdir
import sys
from threading import Thread
from time import sleep

from win32api import GetCursorPos
import wx

from page_keyconfig import KeyConfig
from page_settings import Settings
from profiles import ProfileHandler
from save_load import SaveLoad_Profiles, path_appdata
from tooltips import tooltip_close, tooltip_start, tooltip_stop, \
    tooltip_profiles, tooltip_add_profile, tooltip_remove_profile

sys.stderr = open(path_appdata + "\\error.log", "a")


class MultiThread(Thread):
    '''Class for managing multithreading'''
    def __init__(self, func):
        Thread.__init__(self)
        self.func = func
    
    def run(self):
        self.func(None)


class Frame(wx.Frame, ProfileHandler, SaveLoad_Profiles):
    def __init__(self):
        self.loop_running = False
        
        wx.Frame.__init__(self, None, title="MouseMove")
        
        self.path_profiles = getenv("APPDATA") + "\\GameGuru\\MouseMove\\profiles"
        
        # Creating panel and statusbar
        panel = wx.Panel(self)
        self.statusbar = self.CreateStatusBar()
        
        # Creating sizers
        box = wx.BoxSizer()
        grid = wx.FlexGridSizer(0, 1, 20, 20)
        profiles = wx.FlexGridSizer(0, 3, 10, 10)
        buttons = wx.GridSizer(1, 0, 5, 5)
        
        # Creating widgets
        headline = wx.StaticText(panel, label="MouseMove")
        
        ## Creating profile widgets
        profile_choices = [".".join(path.split(".")[:-1]) for path in listdir(self.path_profiles)]
        lbl_profiles = wx.StaticText(panel, label="Profiles:")
        self.list_profiles = wx.ComboBox(panel, choices=profile_choices, style=wx.CB_SORT | wx.CB_READONLY)
        self.button_remove_profile = wx.Button(panel, size=(26, -1))
        lbl_new_profile = wx.StaticText(panel, label="New profile:")
        self.profile_input = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        button_add_profile = wx.Button(panel, size=(26, -1))
        
        self.button_remove_profile.SetBitmap(wx.Bitmap("icons\\delete.png"))
        button_add_profile.SetBitmap(wx.Bitmap("icons\\add.png"))
        
        # Setting current profile to "Default"
        if len(self.list_profiles.GetItems()) == 0:
            self.list_profiles.SetItems(["Default"])
        self.list_profiles.SetValue("Default")
        
        ## Creating notebook
        self.notebook = wx.Notebook(panel, style=wx.NB_FIXEDWIDTH)
        self.page_settings = Settings(self.notebook)
        self.page_keyconfig = KeyConfig(self.notebook)
        self.notebook.AddPage(self.page_settings, "Settings")
        self.notebook.AddPage(self.page_keyconfig, "Key Config")
        
        ### Init save/load functions
        SaveLoad_Profiles.__init__(self)
                
        ## Creating buttons
        self.start = wx.Button(panel, label="Start")
        self.stop = wx.Button(panel, label="Stop")
        close = wx.Button(panel, label="Quit")
        
        # Adding widgets to sizers
        profiles.AddMany([(lbl_profiles, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT),
                          (self.list_profiles, 0, wx.EXPAND), self.button_remove_profile,
                          (lbl_new_profile, 0, wx.ALIGN_CENTER_VERTICAL),
                          (self.profile_input, 0, wx.EXPAND), button_add_profile])
        
        buttons.AddMany([self.start, self.stop, close])
        grid.AddMany([(headline, 0, wx.ALIGN_CENTER),
                      (profiles, 0, wx.ALIGN_LEFT if getenv("USERNAME") in ["Eirik", "eisv4"] else wx.ALIGN_CENTER),
                      self.notebook, (buttons, 0, wx.ALIGN_CENTER)])
        
        box.Add(grid, 0, wx.ALL, 20)
        panel.SetSizer(box)
        
        # Making headline big
        font = headline.GetFont()
        font.SetPointSize(18)
        font.SetWeight(wx.BOLD)
        headline.SetFont(font)
        
        # Changing font of main buttons
        font = self.start.GetFont()
        font.SetPointSize(10)
        self.stop.SetFont(font)
        close.SetFont(font)
        font.SetWeight(wx.BOLD)
        self.start.SetFont(font)
        
        # Disabling necessary widgets
        self.button_remove_profile.Disable()
        self.stop.Disable()
        
        # Adding tooltips
        self.list_profiles.SetToolTipString(tooltip_profiles)
        button_add_profile.SetToolTipString(tooltip_add_profile)
        self.button_remove_profile.SetToolTipString(tooltip_remove_profile)
        self.start.SetToolTipString(tooltip_start)
        self.stop.SetToolTipString(tooltip_stop)
        close.SetToolTipString(tooltip_close)
        
        # Binding events
        self.Bind(wx.EVT_COMBOBOX, self.change_profile, self.list_profiles)
        self.profile_input.Bind(wx.EVT_KEY_DOWN, self.add_profile_hotkey)
        self.Bind(wx.EVT_BUTTON, self.add_profile, button_add_profile)
        self.Bind(wx.EVT_BUTTON, self.remove_profile, self.button_remove_profile)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.change_page, self.notebook)
        self.Bind(wx.EVT_BUTTON, self.thread_move_loop, self.start)
        self.Bind(wx.EVT_BUTTON, self.stop_motion, self.stop)
        self.Bind(wx.EVT_BUTTON, self.close, close)
        
#         # Setting program-wide hotkeys (NB: NOT global! See page_config.py)
#         id_close_hotkey = wx.NewId()
#         self.Bind(wx.EVT_MENU, self.close, id_close_hotkey)
#         accelerator_table = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, id_close_hotkey)])
#         self.SetAcceleratorTable(accelerator_table)
#         # Not working! Bluh -.-
        
        # Setting unique application identifier (necessary for own taskbr icon)
        windll.shell32.SetCurrentProcessExplicitAppUserModelID("MouseMove")
        
        # Showing window
        self.statusbar.Show()
        self.SetClientSize(panel.GetBestSize())
        self.Center()
        self.Show()
        
        # Initiating memory canvas, for drawing text on icons
        font = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        font.SetFaceName("Segoe UI")
        self.canvas = wx.MemoryDC()
        self.canvas.SetFont(font)
        
        # Updating taskbar icon
        self.update_icon()
    
    
    def change_page(self, event):
        '''Handling actions when user changes page'''
        if self.notebook.GetSelection() == 1:
            self.page_keyconfig.unregister_hotkeys()
        else:
            self.page_keyconfig.register_hotkeys(None)
    
    
    def update_icon(self):
        '''Function for updating taskbar icon, showing which profile is currently running.
        WARNING! This function is hacky, due to a bug in wx!'''
        
        # Loading bitmap from file
        if self.loop_running:
            bitmap = wx.Bitmap("icons\\mousemove_running.png")
        else:
            bitmap = wx.Bitmap("icons\\mousemove.png")
        
        # Converting to image and finding unused color.
        # This color is used as text color. We then loop through all pixels, 
        # and set matching pixels (i.e. the text) to opaque (to avoid bug with transparent text)
        image = bitmap.ConvertToImage()
        text_color = wx.Colour(*image.FindFirstUnusedColour(0, 0, 0)[1:])
        
        # Drawing number on bitmap
        self.canvas.SelectObject(bitmap)
        self.canvas.SetTextForeground(text_color)
        self.canvas.DrawText(str(self.list_profiles.FindString(self.list_profiles.GetValue()) + 1), 35, 0)
        
        image = bitmap.ConvertToImage() # Convert to image (needed to get color of pixels)
        for x in range(image.GetWidth()):
            for y in range(image.GetHeight()):
                color = wx.Colour(image.GetRed(x, y), image.GetGreen(x, y), image.GetBlue(x, y))
                # If color matches text color: make opaque and draw intended color
                if color == text_color:
                    image.SetAlpha(x, y, 255)
                    image.SetRGB(x, y, 255, 255, 0)
        
        # Converting to bitmap, then finally to an icon
        bitmap = image.ConvertToBitmap()
        icon = wx.IconFromBitmap(bitmap)
        self.SetIcon(icon)
    
    
    def _move_cursor_absolute(self, x, y):
        '''Setting absolute cursor position'''
        if self.loop_running: # This if-statement helps ensuring that move loop is terminated immediately after stopping
            windll.user32.SetCursorPos(x, y)
            sleep(self.page_settings.interval.GetValue() / 1000.0)
    
    
    def _move_cursor_relative(self, delta_x, delta_y):
        '''Setting relative cursor position'''
        x, y = GetCursorPos()
        self._move_cursor_absolute(x + delta_x, y + delta_y)
    
    
    def thread_move_loop(self, event):
        '''Initiating main loop'''
        if not self.loop_running:
            self.loop_running = True
            MultiThread(self.move_loop).start()
    
    
    def move_loop(self, event):
        '''Running main loop'''
        settings = self.page_settings # For accessing settings
        current_profile = self.list_profiles.GetValue()
        
        
        # Activate indicators showing that the loop is running
        self.update_icon()
        self.statusbar.SetStatusText("Running: " + current_profile)
        self.SetTitle("MouseMove - Running: " + current_profile)
        self.stop.Enable()
        self.start.Disable()
        
        # Hold down left mouse button (if corresponding setting is enabled)
        self.mouse_hold()
        
        
        while self.loop_running:
            ## ------- CALCULATING MOVEMENT AND "GOOD POSITIONS" ------- ##
            # Collecting movement coordinates
            movement = [[y.GetValue() for y in x] for x in settings.coordinates]
            
            if settings.auto_stop.GetValue():
                if settings.movement_relative.GetValue():
                    # Preparing variables
                    cursorpos = GetCursorPos()
                    good_positions = [cursorpos]
                    last_position = cursorpos
                    
                    # Calculate all acceptable cursor positions
                    # (i.e all positions not stopping loop if "press mouse" is checked)
                    for coords in movement:
                        new_coords = tuple([coords[x] + last_position[x] for x in [0, 1]])
                        good_positions.append(new_coords)
                        last_position = new_coords
                
                else:
                    good_positions = [tuple(x) for x in movement]
            ## --------------------------------------------------------- ##
            
            
            ## ------- MOVING CURSOR ------- ##
            # Stop moving if cursor has a "non-good" position
            for coords in movement:
                
                # Making sure the loop termiates as soon as the user stops it
                if not self.loop_running:
                    break
                
                if settings.movement_absolute.GetValue():
                    self._move_cursor_absolute(*coords)
                else:
                    self._move_cursor_relative(*coords)
                
                if settings.auto_stop.GetValue() and GetCursorPos() not in good_positions:
                    self.loop_running = False
                    break
            
            if settings.movement_relative.GetValue():
                self._move_cursor_relative(-sum([x[0] for x in movement]), -sum(x[1] for x in movement))
            ## ----------------------------- ##
    
    
    def stop_motion(self, event):
        '''Stopping main loop'''
        self.loop_running = False
        
        # Release left mouse button
        self.mouse_release()
        
        # Indicate that loop has stopped
        self.update_icon()
        self.statusbar.SetStatusText("")
        self.SetTitle("MouseMove")
        self.stop.Disable()
        self.start.Enable()
    
    
    def mouse_hold(self):
        '''Function for holding left mouse button'''
        if self.page_settings.hold_mouse.GetValue():
            windll.user32.mouse_event(0x2)
    
    
    def mouse_release(self):
        '''Function for releasing left mouse button'''
        if self.page_settings.hold_mouse.GetValue():
            windll.user32.mouse_event(0x4)
    
    
    def toggle_mouse(self, event):
        hold_mouse_setting = self.page_settings.hold_mouse
        
        if self.loop_running:
            # Release mouse button if it's being held down
            if hold_mouse_setting.GetValue():
                windll.user32.mouse_event(0x4)
            # Hold mouse button if it's not being held down
            else:
                windll.user32.mouse_event(0x2)
        
        hold_mouse_setting.SetValue(not hold_mouse_setting.GetValue())
    
    def close(self, event):
        '''Terminating application'''
        self.loop_running = False
        self.Close()


# Starting application
app = wx.App()
Frame()
app.MainLoop()