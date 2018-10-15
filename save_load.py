from os import getenv, mkdir
from os.path import isdir, isfile


path_gameguru = getenv("APPDATA") + "\\GameGuru"
path_appdata = path_gameguru + "\\MouseMove"
path_profiles = path_appdata + "\\profiles\\"

# Creating path_appdata folder
if not isdir(path_gameguru):
    mkdir(path_gameguru)
if not isdir(path_appdata):
    mkdir(path_appdata)
if not isdir(path_profiles):
    mkdir(path_profiles)


class SaveLoad_Keyconfig:
    '''Class for saving and loading key configuration'''
    def __init__(self):
        self.path_keyconfig = path_appdata + "\\keyconfig.txt"
    
    
    def save_keyconfig(self):
        '''Function for saving keymap'''
        with open(self.path_keyconfig, "w") as keyfile:
            keyfile.write(str([[x.GetValue() for x in self.modifiers], [x.GetValue() for x in self.keys]]))
    
    
    def load_keyconfig(self):
        '''Function for loading keymap'''
        if isfile(self.path_keyconfig):
            with open(self.path_keyconfig) as keyfile:
                keyconfig = eval(keyfile.read())
                
                try: # Needed for old config format without crashing program
                    for modifier, value in zip(self.modifiers, keyconfig[0]):
                        modifier.SetValue(value)
                    for key, value in zip(self.keys, keyconfig[1]):
                        key.SetValue(value)
                except:
                    pass
        
        self.register_hotkeys(None)


class SaveLoad_Profiles:
    '''Class for saving and loading setting profiles'''
    def __init__(self):
        # Creating path_appdata folder
        self.path_profiles = path_profiles
        
        # This class is being derived in two other classes.
        # Making sure variables are accessed from the correct superclass
        if hasattr(self, "page_settings"):
            self.owner = self.page_settings
            self.parent = self
        else:
            self.owner = self
            self.parent = self.frame
        
        # Collecting all settings widgets
        self.profile_settings = [self.owner.movement_absolute, self.owner.interval, self.owner.hold_mouse,
                                 self.owner.auto_stop]
        
        
    def save_profile(self, event):
        '''Collecting all settings and saving them to a file'''
        with open(self.path_profiles + self.parent.list_profiles.GetValue() + ".txt", "w") as profile:
            
            # Getting value from all widgets
            settings = [widget.GetValue() for widget in self.profile_settings]
            # Appending all coordinates
            settings.append([[coord.GetValue() for coord in position] for position in self.owner.coordinates])
            
            profile.write(str(settings))
        
        if event != None:    
            event.Skip()
    
    
    def load_profile(self):
        '''Loading all the current profile's settings from a file and apply them in their respective widgets'''
        
        # Clearing list of coordinates, and re-adding headline
        self.owner.motionctrl.Clear(True)
        self.owner._add_motionctrl_headline()
        
        with open(self.path_profiles + self.parent.list_profiles.GetValue() + ".txt") as profile:
            try:
                settings = eval(profile.read())
            except:
                return
            
            # Applying values to settings widgets
            for widget, value in zip(self.profile_settings, settings[:-1]):
                widget.SetValue(value)
            
            # Making absolute and relative checkboxes having opposite values
            self.owner.movement_relative.SetValue(not settings[0])
            
            # Adding empty coordinates to list
            for coord in settings[-1]:  # @UnusedVariable
                self.owner.add_coords(None)
            
            # Filling in all coordinate values
            for row, position in zip(self.owner.coordinates, settings[-1]):
                for widget, coord in zip(row, position):
                    widget.SetValue(coord)
        