from os import remove

import wx


class ProfileHandler:
    def add_profile(self, event):
        '''Adding a new profile'''
        new_profile = self.profile_input.GetValue()
        
        if len(new_profile) > 0:            
            # Adding profile (making sure it's not already in the list)
            profiles = self.list_profiles.GetItems()
            if new_profile not in profiles:
                profiles.append(new_profile)
                self.list_profiles.SetItems(profiles)
                self.list_profiles.SetValue(new_profile)
                self.save_profile(None)
            
            self.profile_input.Clear()
            self.button_remove_profile.Enable()
            
            self.change_profile(None)
    
    
    def add_profile_hotkey(self, event):
        '''Adding a new profile by pressing enter in the input field'''
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.add_profile(None)
        else:
            event.Skip()
    
    
    def remove_profile(self, event):
        '''Removing the currently selected profile'''
        old_profile = self.list_profiles.GetValue()
        
        if old_profile != "Default": # Making sure the default profile doesn't get removed!
            profiles = self.list_profiles.GetItems()
            
            # Remove profile from list
            if old_profile in profiles:
                profiles.remove(old_profile)
            self.list_profiles.SetItems(profiles)
            
            # Removing corresponding system file
            remove(self.path_profiles + old_profile + ".txt")
            
            # Switch back to default
            self.list_profiles.SetValue("Default")
            self.change_profile(None)
    
    
    def change_profile(self, event):
        '''Function for switching profile'''
        # Loading settings and updating taskbar icon with correct number
        self.page_settings.coordinates = []
        self.load_profile()
        self.update_icon()
        
        # User can never remove the default profile!
        if self.list_profiles.GetValue() == "Default":
            self.button_remove_profile.Disable()
        else:
            self.button_remove_profile.Enable()
        
        # Update "running" icon, title and statusbar with correct number
        if self.loop_running:
            current_profile = self.list_profiles.GetValue()
            self.statusbar.SetStatusText("Running: " + current_profile)
            self.SetTitle("MouseMove - Running: " + current_profile)
    
    
    def next_profile(self, event):
        '''Function for changing profile (actually, selecting the next in the list) via hotkey'''
        all_profiles = self.list_profiles.GetItems()
        
        if len(all_profiles) > 1:
            current_profile = self.list_profiles.GetValue()
            
            if current_profile == all_profiles[-1]:
                self.list_profiles.SetSelection(0)
            else:
                self.list_profiles.SetSelection(self.list_profiles.FindString(current_profile) + 1)
            self.change_profile(None)