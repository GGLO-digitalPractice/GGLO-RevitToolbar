## File: room_utils.py

from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, CurveLoop
from Autodesk.Revit.DB.Architecture import Room
from Autodesk.Revit.DB import SpatialElementBoundaryOptions, Transaction
from collections import defaultdict

# Access current Revit document
doc = __revit__.ActiveUIDocument.Document

# Function to get room boundaries
def get_room_boundaries(rooms):
    boundaries = {}
    options = SpatialElementBoundaryOptions()

    for room in rooms:
        boundary = room.GetBoundarySegments(options)
        if boundary:  # If there is a boundary
            boundaries[room] = [seg.GetCurve() for seg in boundary[0]]

    for room, boundary in boundaries.items():

        for curve in boundary:
            if curve is Line:
                print("Line from {} to {}".format(curve.GetEndPoint(0), curve.GetEndPoint(1)))
            elif curve is Arc:
                print("Arc with center {}, start {}, end {}, radius {}, and angle {}"
                      .format(curve.Center, curve.GetEndPoint(0), curve.GetEndPoint(1), curve.Radius, curve.Angle))
            elif curve is Ellipse:
                print("Ellipse with center {}, radii {}, and rotation angle {}"
                      .format(curve.Center, (curve.RadiusX, curve.RadiusY), curve.RotationAngle))

    return boundaries


# Function to get rooms with same SpaceType
def merge_rooms_by_param(rooms, param_name):
    # Group rooms by parameter
    grouped_rooms = defaultdict(list)
    for room in rooms:
        param = room.LookupParameter(param_name)
        if param:
            param_value = param.AsValueString()  # This gets the value as a string
            print("Parameter value: {}".format(param_value))
        else:
            print("Parameter {} does not exist for the room.".format(param_name))        
        print(param)
    # Create new boundaries
    new_boundaries = {}
    for param_val, rooms in grouped_rooms.items():
        new_boundary = CurveLoop()
        for room in rooms:
            boundary = get_room_boundaries([room])[room]
            for curve in boundary:
                new_boundary.Append(curve)
        new_boundaries[param_val] = new_boundary

    return new_boundaries
