## File: boundaries_script.py

# Standard library imports
from System import Enum
from System.Collections.Generic import List
from collections import defaultdict
import logging

# Revit imports
import clr
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

from pyrevit import forms

# Import Revit API UI
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import UIApplication

# Local application/library specific imports
import room_utils

# Set up doc and uidoc variables
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

# Get the current view
current_view = uidoc.ActiveView

# Get all the walls in the current view
collector = FilteredElementCollector(doc, current_view.Id)

# Start the transaction
# t = Transaction(doc, 'Create area boundaries from walls')
# t.Start()

# Initialize a counter for the number of lines created
num_lines_created = 0

def get_parameter_value_by_name(element, name):
    param = element.LookupParameter(name)
    if param:
        if param.StorageType == StorageType.Double:
            return param.AsDouble()  # Return as double if the parameter type is a number
        else:
            return param.AsString()  # Otherwise, return as string
    else:
        return None  # Return None if the parameter is not found

# Collect all elements of different categories
levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()

# Only wall instances, not types
walls = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()

# Only placed rooms
rooms = [r for r in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements() if r.Area > 0]

# Property Lines
property_lines = FilteredElementCollector(doc).OfClass(clr.GetClrType(Autodesk.Revit.DB.PropertyLine)).ToElements()

# AreaSchemes
area_schemes = FilteredElementCollector(doc).OfClass(AreaScheme).ToElements()

# Initialize a list to store area scheme names
area_scheme_names = []

# Loop through each area scheme and store its name
for area_scheme in area_schemes:
    area_scheme_names.append(area_scheme.Name)

# Create a nested dictionary to hold the walls, grouped by level and function
walls_by_level_and_function = defaultdict(lambda: defaultdict(list))
rooms_by_level_and_space_type = defaultdict(lambda: defaultdict(list))

# Group walls by level and function
for wall in walls:
    level = doc.GetElement(wall.LevelId).Name if wall.LevelId else 'No Level'
    function = wall.WallType.Function
    walls_by_level_and_function[level][str(function)].append(wall)

# Group rooms by level and SpaceType
for room in rooms:
    level = doc.GetElement(room.LevelId).Name if room.LevelId else 'No Level'
    space_type = room.LookupParameter('SpaceType').AsString() if room.LookupParameter('SpaceType') else 'No SpaceType'
    rooms_by_level_and_space_type[level][space_type].append(room)

# Print the results
for level, walls_by_function in walls_by_level_and_function.items():
    print("\nLevel: {}".format(level))
    for function, walls in walls_by_function.items():
        print("  Function: {}".format(function))
        for wall in walls:
            print("    Wall: {}".format(wall.Id.IntegerValue))

for level, rooms_by_space_type in rooms_by_level_and_space_type.items():
    print("\nLevel: {}".format(level))
    for space_type, rooms in rooms_by_space_type.items():
        print("  Space Type: {}".format(space_type))
        for room in rooms:
            print("    Room: {}".format(room.Id.IntegerValue))

# Create a list to store the results
property_line_results = []

for property_line in property_lines:
    name = get_parameter_value_by_name(property_line, "Name")
    area = get_parameter_value_by_name(property_line, "Area")
    if name is not None and area is not None:
        property_line_results.append("Name: {}, Area: {}, ID: {}".format(name, area, property_line.Id))

# Print the results
if len(property_line_results) > 0:
    print("\nProperty Lines:")
    for result in property_line_results:
        print(result)
else:
    forms.alert("No Property Lines found.", title="Warning", warn_icon=True)
    
# Print the list of area scheme names
print("\nArea Schemes:")
print(area_scheme_names)
# try:
    # # Test the functions
    # param_name = 'SpaceType'
    # boundaries = room_utils.merge_rooms_by_param(rooms, param_name)
    
    # # Create a new Area Boundary based on the exterior line
    # for boundary in boundaries:
        # print(boundary)
        # doc.Create.NewAreaBoundaryLine(current_view.SketchPlane, boundary, current_view)
        # num_lines_created += 1

# except Exception as e:
    # logging.error("Exception occurred", exc_info=True)
    # t.RollBack()
# else:
    # t.Commit()
    # print("\nSuccess! Created {} Area Boundary Lines.".format(num_lines_created))
