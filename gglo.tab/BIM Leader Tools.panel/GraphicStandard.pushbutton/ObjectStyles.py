#ObjectStyles.py

import clr
from pyrevit import forms

# Import Revit API
clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import Color, Transaction, FilteredElementCollector, TextNoteType, DimensionType, BuiltInParameter

# Import your script utilities
import script_utils
import font_utils

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument


# def hex_to_rgb(value):
    # value = value.lstrip('#')
    # length = len(value)
    # return tuple(int(value[i:i + length // 3], 16) for i in range(0, length, length // 3))
    
def system_color_to_rgb(system_color):
    return (system_color.R, system_color.G, system_color.B)

def modify_font(chosen_font, doc):
    text_note_types = FilteredElementCollector(doc).OfClass(TextNoteType).ToElements()
    dimension_types = FilteredElementCollector(doc).OfClass(DimensionType).ToElements()

    all_types = list(text_note_types)  # Convert to Python list
    all_types.extend(list(dimension_types))  # Convert to Python list and extend

    for element_type in all_types:
        param = element_type.get_Parameter(BuiltInParameter.TEXT_FONT)
        if param:
            param.Set(chosen_font)

# Now in color_setup:
def color_setup(system_color):
    if not system_color:
        print("No color selected. Exiting script.")
        sys.exit()

    r, g, b = system_color_to_rgb(system_color)
    color = Color(r, g, b)
    red = Color(128,0,0)
    npb = Color(164, 221, 237)

    search_terms_colors = [
        (["Tag", "View", "Grid", "Symbol", "Section Line", "Mark", "Annotation", "Stair", "Matchline", "Head", "Callout"], color),
        (["Revision"], red),
        (["Guide Grid", "Reference", "Boxes", "Plan Region"], npb)
        ]
    return search_terms_colors
    
def run_object_styles(chosen_font, chosen_color):
    search_terms_colors = color_setup(chosen_color)
    t = Transaction(doc, "Change color and font of annotations")
    t.Start()
    try:
        script_utils.change_color_of_categories(doc, search_terms_colors)
        script_utils.change_color_of_types(doc, color)

        # chosen_font = font_utils.ask_for_font()
        if chosen_font:
            modify_font(chosen_font, doc)

        t.Commit()
        print("Annotation Categories' colors and fonts have been successfully updated")
        uidoc.RefreshActiveView()

    except Exception as ex:
        print("Error:", ex)
        t.RollBack()
