## File: boundaries_script.py

# Standard library imports
from System.Collections.Generic import List
import logging
from pyrevit import forms

# Revit imports
import clr
clr.AddReference('RevitAPI')

from Autodesk.Revit.DB import BuiltInCategory, FilteredElementCollector, Transaction, Line, XYZ, ElementId
from Autodesk.Revit.UI import UIDocument, UIApplication
from System.Collections.Generic import List

# Local application/library specific imports
import wall_utils

# Set up doc and uidoc variables
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

# Get the current view
current_view = uidoc.ActiveView

# Get all the walls in the current view
collector = FilteredElementCollector(doc, current_view.Id)
walls = collector.OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
print("Current view: {}".format(current_view.Name))
print("Number of walls: {}".format(len(walls)))

def prompt_for_boundary_type():
    """Prompt the user to select a boundary type."""
    boundary_types = ['Gross', 'FAR', 'NSF']
    selected_boundary = forms.CommandSwitchWindow.show(
        boundary_types,
        message='Select the type of boundary:'
    )
    return selected_boundary

# Start the transaction
t = Transaction(doc, 'Create area boundaries from walls')
print("Starting Transaction...")
t.Start()
print("Transaction started.")


# Initialize a counter for the number of lines created
num_lines_created = 0

##try:
print("Starting the loop for generating exterior lines...")
wall_groups = wall_utils.group_walls(walls)
print("Number of wall groups: {}".format(len(wall_groups)))
print(wall_groups)
# Convert the list of wall ids to wall elements
wall_groups_elements = [[doc.GetElement(ElementId(id)) for id in group] for group in wall_groups]
print(wall_groups_elements)
# Prompt user for boundary type
selected_boundary_type = prompt_for_boundary_type()

if not selected_boundary_type:
    print("User cancelled or did not make a selection. Exiting script.")
    # Optionally, exit the script here if needed
else:
    # Use the selected_boundary_type to determine location of lines
    if selected_boundary_type == 'Gross':
        # Set your logic for Gross
        boundary_lines = wall_utils.get_wall_exterior_lines(wall_groups_elements)
        print(boundary_lines)
    elif selected_boundary_type == 'FAR':
        # Set your logic for FAR
        print("FAR definition not yet implemented.")
    elif selected_boundary_type == 'NSF':
        # Set your logic for NSF
        print("NSF definition not yet implemented.")
# Then pass the flattened list to your function

try:
    # Create a new Area Boundary based on the exterior line
    for group_lines in boundary_lines:
        for boundary_line in group_lines:
            doc.Create.NewAreaBoundaryLine(current_view.SketchPlane, boundary_line, current_view)
            num_lines_created += 1
            print("Created line #{}".format(num_lines_created))
except Exception as e:
    logging.error("Exception occurred", exc_info=True)
    t.RollBack()
else:
    t.Commit()
    print("Transaction committed.")
    print("\nSuccess! Created {} Area Boundary Lines.".format(num_lines_created))

