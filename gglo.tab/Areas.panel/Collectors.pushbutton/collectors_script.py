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

# Collect all the walls in the project
walls = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()

for wall in walls:
    level = doc.GetElement(wall.LevelId).Name if wall.LevelId else 'No Level'
    function = wall.WallType.Function
    walls_by_level_and_function[level][str(function)].append(wall)

# Print the results
for level, walls_by_function in walls_by_level_and_function.items():
    print("\nLevel: {}".format(level))
    for function, walls in walls_by_function.items():
        print("  Function: {}".format(function))
        for wall in walls:
            print("    Wall: {}".format(wall.Id.IntegerValue))

# # Sort levels by elevation
# levels = sorted(levels, key=lambda level: level.Elevation)

# # Group walls and rooms by level
# walls_by_level = {level.Name: [wall for wall in walls if wall.LevelId == level.Id] for level in levels}
# rooms_by_level = {level.Name: [room for room in rooms if room.LevelId == level.Id] for level in levels}



# # Print elements grouped by levels
# for level in levels:
    # wall_list = walls_by_level[level.Name]
    # room_list = rooms_by_level[level.Name]
    
    # if wall_list or room_list:
        # level_results = ["\nLevel: {}".format(level.Name)]
    
        # if wall_list:
            # wall_results = ["\nWalls:"]
            # for wall in wall_list:
                # wall_results.append("{}: {}".format(wall.Name, wall.Id))
            # level_results.extend(wall_results)
        
        # if room_list:
            # room_results = ["\nRooms:"]
            # for room in room_list:
                # room_results.append("Room: {}".format(room.Number))
            # level_results.extend(room_results)
        
        # results_by_level.append(level_results)

# Initialize lists for storing results
results_by_level = []
property_line_results = []

for property_line in property_lines:
    name = get_parameter_value_by_name(property_line, "Name")
    area = get_parameter_value_by_name(property_line, "Area")
    if name is not None and area is not None:
        property_line_results.append("Name: {}, Area: {}, ID: {}".format(name, area, property_line.Id))

# Now the results are stored in the lists results_by_level and property_line_results
# You can print them out, write to a file, etc.
for result in results_by_level:
    print('\n'.join(result))

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



# merged_boundaries = room_utils.merge_rooms_by_param(rooms, "SpaceType")
# print(merged_boundaries)