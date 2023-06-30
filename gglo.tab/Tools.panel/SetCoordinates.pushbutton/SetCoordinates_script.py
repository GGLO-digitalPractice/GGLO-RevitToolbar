"""Enables standard procedure for setting shared coordinates"""

__title__ = 'Set Coordinates'
__author__ = 'Sean Burke'

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import Transaction, XYZ, ViewType, FilteredElementCollector, BuiltInCategory

# Get the current document and active view
doc = __revit__.ActiveUIDocument.Document
view = doc.ActiveView

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
        new_coordinates = XYZ(100, 200, 0)  # Replace with desired coordinates

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
