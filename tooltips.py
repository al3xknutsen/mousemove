# Main tooltips
tooltip_profiles = '''List of profiles.
A profile is basically a setup of settings. Profiles makes it easy to switch between different setups.'''
tooltip_add_profile = '''Add a profile and apply all current settings to it (not including hotkeys).
To add, write a name in the text field (to the left), and then press this button.'''
tooltip_remove_profile = "Removes the currently selected profile."
tooltip_start = "Start moving the cursor."
tooltip_stop = "Stop moving the cursor."
tooltip_close = "Exit the program."

# Settings tooltips
tooltip_movement_absolute = "The cursor will be moved to the given coordinates."
tooltip_movement_relative = "The cursor will be moved the given amount of pixels from its current position."
tooltip_x = "Movement along the X-axis (horizontally)"
tooltip_y = "Movement along the Y-axis (vertically)"
tooltip_record_coord = "Record a single coordinate."
tooltip_delete_coord = "Delete this coordinate."
tooltip_add = "Add a new coordinate for the cursor to move to."
tooltip_clear = "Reset all coordinates to 0."
tooltip_record = '''Record cursor positions, and input them into the list when clicking.
- If movement is set to absolute, it will input a coordinate in the list for every mouse click.
- If movement is set to relative, it will behave similarly, except the first click
will be used as an origin (and not as a coordinate)'''
tooltip_interval = '''Time it takes (in milliseconds) for the cursor to move to the next position
(1 second = 1000 milliseconds)'''
tooltip_hold_mouse = "The left mouse button will be held while moving the cursor."
tooltip_auto_stop = "The program will stop moving the cursor if the mouse is moved manually."