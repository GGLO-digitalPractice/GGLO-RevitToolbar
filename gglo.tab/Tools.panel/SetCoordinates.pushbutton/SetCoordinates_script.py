"""Sets the coordinates of the project base point to the selected benchmark"""

__title__ = 'Set Coordinates'
__author__ = 'Sean Burke'

import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *

# Standard library imports
from System.Collections.Generic import List
from pyrevit import forms
from pyrevit.forms import WPFWindow
import logging

# Get the current document and active view
doc = __revit__.ActiveUIDocument.Document
view = __revit__.ActiveUIDocument.ActiveView
uidoc = __revit__.ActiveUIDocument

# Prompt user for coordinates
y = forms.ask_for_string(default="0", prompt="Enter North Coordinate") 
x = forms.ask_for_string(default="0", prompt="Enter East Coordinate")
z = forms.ask_for_string(default="0", prompt="Enter Height Elevation")

x = float(x)
y = float(y)
z = float(z)

selected_benchmark = XYZ(x, y, z)

print("Coordinates: {}".format(selected_benchmark))
# Collect Survey points and change the clip state to unclipped
survey_point = BasePoint.GetSurveyPoint(doc)
print(survey_point)

# Start a transaction
t = Transaction(doc, 'Unclip Survey Points')
t.Start()

# Check if the active view is a plan view
if view.ViewType == ViewType.FloorPlan:
    # Retrieve Base Point
    base_points = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_ProjectBasePoint).ToElements()

    # Check if a base point exists
    if base_points:
        # Get the first base point from the list
        base_point = base_points[0]

        # Get the XYZ location of the base point
        base_point_location = base_point.Position

        # Set new coordinates for the base point
        new_coordinates = (selected_benchmark)  # Replace with desired coordinates

        with Transaction(doc, 'Set Base Point Coordinates') as t:
            t.Start()
            project_location = doc.ActiveProjectLocation
            project_position = project_location.GetProjectPosition(base_point_location)
            project_position.EastWest = new_coordinates.X
            project_position.NorthSouth = new_coordinates.Y
            project_position.Elevation = new_coordinates.Z
            project_location.SetProjectPosition(base_point_location, project_position)
            t.Commit()

        print("Base point coordinates set.")
    else:
        print("No base point found in the project.")
else:
    print("The active view is not a plan view.")
