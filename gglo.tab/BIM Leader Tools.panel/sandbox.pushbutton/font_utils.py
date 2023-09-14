# font_utils.py
# from pyrevit import forms

# chosen_font = None

# def ask_for_font():
    # global chosen_font  # Declare it as a global variable
    
    # # Prompt the user for font name
    # selected_font = forms.ask_for_string("Enter Font Name:")
    # if selected_font:
        # chosen_font = selected_font.strip()
    # return chosen_font
    
import clr
clr.AddReference("System.Drawing")

from System.Drawing import Text
from pyrevit import forms

chosen_font = None

def ask_for_font():
    global chosen_font  # Declare it as a global variable
    
    # Fetch all system font families
    installed_fonts = Text.InstalledFontCollection().Families
    available_fonts = [font.Name for font in installed_fonts]

    # Use pyRevit's forms to show a selection list
    # Adding the 'subtitle' parameter to provide additional instructions
    selected_font = forms.SelectFromList.show(available_fonts, 
                                              title="Select a Font", 
                                              subtitle="Note: Not all installed fonts listed are compatible with Revit.")

    if selected_font:
        chosen_font = selected_font if isinstance(selected_font, str) else selected_font[0] # SelectFromList returns a list. Since we're selecting one item, get the first item from the list.
        print("Font:", chosen_font)
    return chosen_font

