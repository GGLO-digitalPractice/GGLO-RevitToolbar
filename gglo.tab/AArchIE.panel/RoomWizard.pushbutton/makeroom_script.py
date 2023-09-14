import clr
from Autodesk.Revit.DB import XYZ, Line, Transaction, FilteredElementCollector, Wall, WallType, Level, FloorType, CurveArray, CeilingType, UV, CurveLoop, Floor, Ceiling, BuiltInParameter
from System.Collections.Generic import List

# Get the current document
doc = __revit__.ActiveUIDocument.Document

# Define the room dimensions
length = 25  # example value, replace with input
width = 15  # example value, replace with input
height = 9.5  # example value, replace with input

# Start a transaction
t = Transaction(doc, 'Create Room')

try:
    t.Start()

    # ... your code here ...

    # Create the walls
    wall_type = FilteredElementCollector(doc).OfClass(WallType).FirstElement()
    level = FilteredElementCollector(doc).OfClass(Level).FirstElement()

    wall1 = Wall.Create(doc, Line.CreateBound(XYZ(0, 0, 0), XYZ(length, 0, 0)), wall_type.Id, level.Id, height, 0, False, False)
    wall2 = Wall.Create(doc, Line.CreateBound(XYZ(length, 0, 0), XYZ(length, width, 0)), wall_type.Id, level.Id, height, 0, False, False)
    wall3 = Wall.Create(doc, Line.CreateBound(XYZ(length, width, 0), XYZ(0, width, 0)), wall_type.Id, level.Id, height, 0, False, False)
    wall4 = Wall.Create(doc, Line.CreateBound(XYZ(0, width, 0), XYZ(0, 0, 0)), wall_type.Id, level.Id, height, 0, False, False)

    # Get the Creation object
    creation = doc.Create

    # Create the floor
    floor_type = FilteredElementCollector(doc).OfClass(FloorType).FirstElement()
    curve_loop = CurveLoop.Create([wall1.Location.Curve, wall2.Location.Curve, wall3.Location.Curve, wall4.Location.Curve])
    curve_loops = List[CurveLoop]([curve_loop])
    floor = Floor.Create(doc, curve_loops, floor_type.Id, level.Id)

    # Create the ceiling
    ceiling_type = FilteredElementCollector(doc).OfClass(CeilingType).FirstElement()

    # Get the wall thickness
    wall_thickness = wall_type.Width

    # Offset by half the wall thickness
    offset = wall_thickness / 2
    first = XYZ(offset, offset, 0)
    second = XYZ(length - offset, offset, 0)
    third = XYZ(length - offset, width - offset, 0)
    fourth = XYZ(offset, width - offset, 0)

    curve_loop = CurveLoop.Create([Line.CreateBound(first, second), Line.CreateBound(second, third), Line.CreateBound(third, fourth), Line.CreateBound(fourth, first)])
    curve_loops = List[CurveLoop]([curve_loop])
    ceiling = Ceiling.Create(doc, curve_loops, ceiling_type.Id, level.Id)

    
    # Set the elevation of the ceiling
    elevation = height  # example value, replace with input
    param = ceiling.get_Parameter(BuiltInParameter.CEILING_HEIGHTABOVELEVEL_PARAM)
    param.Set(elevation)
    
    # Place a room
    room = doc.Create.NewRoom(level, UV(length / 2, width / 2))

    t.Commit()
    
except Exception as ex:
    if t.HasStarted():
        t.RollBack()
    print('Error:', ex)
    

# Dispose of the transaction
t.Dispose()
