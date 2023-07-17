import clr

# Import Revit API
clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import Color, Transaction

# Import your script utilities
import script_utils

# get the current document
doc = __revit__.ActiveUIDocument.Document

# Set up the colors
blue = Color(0,128,255)  # Color is defined with RGB values
red = Color(128,0,0)
npb = Color(164, 221, 237)

# Set up the category seearch term / color combinations
search_terms_colors = [
    (["Revision"], red),  # Red
    (["Tag", "View", "Grid", "Symbol", "Section Line", "Mark", "Annotation", "Stair", "Matchline", "Head", "Callout"], blue),  # Blue
    (["Guide Grid", "Reference", "Boxes", "Plan Region"], npb)  # Non-Photo Blue
    ]

# Start a new transaction
t = Transaction(doc, "Change color of selected annotation categories")
t.Start()

try:
    script_utils.change_color_of_categories(doc, search_terms_colors)
    script_utils.change_color_of_types(doc, blue)
    
    # If successful, commit the transaction
    t.Commit()
except Exception as ex:
    # If there is any error, roll back the transaction
    print("Error: ", ex)
    t.RollBack()

