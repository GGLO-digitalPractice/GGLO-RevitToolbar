## File: boundaries_script.py

# Standard library imports
from System.Collections.Generic import List
import logging

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

# Start the transaction
t = Transaction(doc, 'Create area boundaries from walls')
t.Start()

# Initialize a counter for the number of lines created
num_lines_created = 0

try:
    wall_groups = wall_utils.group_walls(walls)
    
    # Convert the list of wall ids to wall elements
    wall_groups_elements = [[doc.GetElement(ElementId(id)) for id in group] for group in wall_groups]
    
    # Then pass the flattened list to your function
    exterior_lines = wall_utils.get_wall_exterior_lines(wall_groups_elements)
    print(exterior_lines)
    # Create a new Area Boundary based on the exterior line
    for group_lines in exterior_lines:
        for exterior_line in group_lines:
            doc.Create.NewAreaBoundaryLine(current_view.SketchPlane, exterior_line, current_view)
            num_lines_created += 1

except Exception as e:
    logging.error("Exception occurred", exc_info=True)
    t.RollBack()
else:
    t.Commit()
    print("\nSuccess! Created {} Area Boundary Lines.".format(num_lines_created))
