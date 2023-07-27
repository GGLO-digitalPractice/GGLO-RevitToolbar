## File: wall_utils.py

# Import relevant libraries
import clr
from clr import StrongBox
clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import (
    BuiltInParameter, 
    LocationCurve,
    IntersectionResultArray,
    SetComparisonResult,
    XYZ,
    Line)

# Set up doc and uidoc variables
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

# Define your functions here

def get_wall_exterior_lines(wall_groups):
    exterior_lines = []
    
    for walls in wall_groups:
        group_lines = []
        for i in range(len(walls)):
            wall = walls[i]
            wall_type = wall.WallType
            auto_embed_param = wall_type.get_Parameter(BuiltInParameter.ALLOW_AUTO_EMBED)
            if auto_embed_param and auto_embed_param.AsInteger() == 0:
                location_curve = wall.Location
                if isinstance(location_curve, LocationCurve):
                    wall_width = wall_type.get_Parameter(BuiltInParameter.WALL_ATTR_WIDTH_PARAM).AsDouble()
                    direction = location_curve.Curve.Direction
                    normal = XYZ.BasisZ.CrossProduct(direction)
                    if wall.Flipped:
                        normal = -normal
                    start_point = location_curve.Curve.GetEndPoint(0) + normal * wall_width / 2
                    end_point = location_curve.Curve.GetEndPoint(1) + normal * wall_width / 2
                    exterior_line = Line.CreateBound(start_point, end_point)
                    group_lines.append(exterior_line)

        # Adjust line endpoints
        for i in range(len(group_lines) - 1):
            current_line = group_lines[i]
            next_line = group_lines[i+1]
            infinite_line1 = Line.CreateUnbound(current_line.GetEndPoint(0), current_line.Direction)
            infinite_line2 = Line.CreateUnbound(next_line.GetEndPoint(0), next_line.Direction)

            intersection_pt = intersect(infinite_line1, infinite_line2)
            if intersection_pt is not None:
                # Check that intersection is within 2 feet of original endpoints
                if (intersection_pt - current_line.GetEndPoint(1)).GetLength() <= 2.0 or (intersection_pt - next_line.GetEndPoint(0)).GetLength() <= 2.0:
                    # set end of current line to intersection
                    current_line = Line.CreateBound(current_line.GetEndPoint(0), intersection_pt)
                                
                    # set start of next line to intersection
                    next_line = Line.CreateBound(intersection_pt, next_line.GetEndPoint(1))
                                
                    # replace in the list
                    group_lines[i] = current_line
                    group_lines[i+1] = next_line
        
        exterior_lines.append(group_lines)
    
    return exterior_lines

def intersect(line1, line2):
    results = StrongBox[IntersectionResultArray]()
    result = line1.Intersect(line2, results)
    if result == SetComparisonResult.Overlap:
        return results.Value[0].XYZPoint
    else:
        return None


        
def are_walls_connected(wall1, wall2):
    # Determine if two walls are connected based on their location curves
    curve1 = wall1.Location.Curve
    curve2 = wall2.Location.Curve

    # Check if the end points of the curves are close enough to be considered connected
    return (curve1.GetEndPoint(0).IsAlmostEqualTo(curve2.GetEndPoint(0)) or
            curve1.GetEndPoint(0).IsAlmostEqualTo(curve2.GetEndPoint(1)) or
            curve1.GetEndPoint(1).IsAlmostEqualTo(curve2.GetEndPoint(0)) or
            curve1.GetEndPoint(1).IsAlmostEqualTo(curve2.GetEndPoint(1)))


def group_walls(walls):
    wall_groups = []

    remaining_walls = list(walls)  # Copy list so we can modify it while iterating

    while remaining_walls:
        current_wall = remaining_walls.pop(0)  # Start with the first wall
        current_group = [current_wall.Id.IntegerValue]  # Initialize group with current wall's Id

        next_wall = find_next_wall(current_wall, remaining_walls)

        # While we can find a connected wall that isn't already in the group
        while next_wall and next_wall.Id.IntegerValue not in current_group:
            current_group.append(next_wall.Id.IntegerValue)  # Add the next wall to the group
            remaining_walls.remove(next_wall)  # Remove the wall from the remaining walls

            # Find the next wall connected to the current one
            next_wall = find_next_wall(next_wall, remaining_walls)

        # Once we can't find any more connected walls, we know we've completed the loop
        wall_groups.append(current_group)

    return wall_groups

def find_next_wall(current_wall, remaining_walls):
    for other_wall in remaining_walls:
        if are_walls_connected(current_wall, other_wall):
            return other_wall
    return None


def get_wall_compound_structure_location(wall):
    # Get the wall type
    wall_type = wall.WallType
    # Get the compound structure
    cs = wall_type.GetCompoundStructure()

    # Make sure the wall has a compound structure
    if cs is None:
        return None

    # Create a list to hold the layer locations
    layer_locations = []

    # Get the width of the wall (the distance from the core face to the exterior face)
    wall_width = cs.GetWidth()

    # Get the first and last core layer indices
    first_core_layer_index = cs.GetFirstCoreLayerIndex()
    last_core_layer_index = cs.GetLastCoreLayerIndex()

    # Iterate over each layer in the compound structure
    for i in range(cs.LayerCount):
        # Get the width of the layer
        layer_width = cs.GetLayerWidth(i)

        # Calculate the location of the layer relative to the core face
        # (assuming the core face is at location 0)
        layer_location = (wall_width - layer_width) / 2

        # Get the function of the layer
        layer_function = cs.GetLayerFunction(i)

        # Add the layer information to the list
        layer_locations.append({
            'Layer Index': i,
            'Layer Location': layer_location,
            'Layer Function': str(layer_function),
            'First Core Layer Index': first_core_layer_index,
            'Last Core Layer Index': last_core_layer_index
        })

    return layer_locations
    
def get_wall_data(walls):
    # Initialize a dictionary to hold wall type data
    wall_type_data = {}

    # Iterate over each wall
    for wall in walls:
        # Get the wall type
        wall_type = wall.WallType.Kind.ToString()
        # If the wall type isn't in the dictionary, add it
        if wall_type not in wall_type_data:
            wall_type_data[wall_type] = {
                'Element IDs': [],
                'Compound Layer Info': get_wall_compound_structure_location(wall)
            }
        # Append the wall's element ID to the wall type's list of element IDs
        wall_type_data[wall_type]['Element IDs'].append(wall.Id)

    return wall_type_data