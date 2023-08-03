import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import *
from System.Collections.Generic import List

doc = __revit__.ActiveUIDocument.Document

# Start a transaction
t = Transaction(doc, 'Create Area Boundary Lines')
t.Start()

# Create a filter collector to collect all walls in the document
collector = FilteredElementCollector(doc)
walls = collector.OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()

# Create a filter collector to collect all levels in the document
levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()

# Create a filter collector to collect all area schemes in the document
area_schemes = FilteredElementCollector(doc).OfClass(AreaScheme).ToElements()

# Get the Gross Area Scheme
gross_area_scheme = next((s for s in area_schemes if s.Name == "Gross Building"), None)

# Specify the area plan view for creating area boundary lines
view = doc.ActiveView  # Update this line with the desired area plan view

# Create lists to store boundary lines and sketch planes
boundary_lines = []
sketch_planes = []

# Iterate over all walls
for wall in walls:
    # Check if the wall is exterior by its function parameter
    wall_function = wall.WallType.Function
    if wall_function == "Exterior":
        # Get the location curve of the wall
        location_curve = wall.Location.Curve
        curves = [location_curve]

        # Get the wall's level
        wall_level_id = wall.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT).AsElementId()

        for level in levels:
            if level.Id == wall_level_id:
                # Create a sketch plane for the wall's level
                sketch_plane = SketchPlane.Create(doc, level.Id)
                sketch_planes.append(sketch_plane)

                # Create a curve array for each wall location curve
                curve_array = CurveArray()
                for curve in curves:
                    curve_array.Append(curve)

                # Create the area boundary line from the curve
                area_boundary_line = doc.Create.NewAreaBoundaryLine(sketch_plane, curve_array, view)
                boundary_lines.append(area_boundary_line)

# Create the area with the boundary lines
if gross_area_scheme is not None:
    area = Area.Create(doc, view.Id, gross_area_scheme.Id, sketch_planes, List[Curve](boundary_lines))

t.Commit()  # Don't forget to commit the transaction
print("Transaction committed.")
