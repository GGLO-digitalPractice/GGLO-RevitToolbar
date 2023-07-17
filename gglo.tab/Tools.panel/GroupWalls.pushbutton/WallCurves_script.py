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

# Iterate over all walls
for wall in walls:
    # Check if the wall is exterior by its function parameter
    wall_function = wall.get_Parameter(BuiltInParameter.FUNCTION_PARAM).AsInteger()
    if wall_function == 1: # 1 represents exterior in FUNCTION_PARAM
        # Get the location curve of the wall
        location_curve = wall.Location.Curve
        curves = [location_curve]

        # Get the wall's level
        wall_level_id = wall.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT).AsElementId()
        
        for level in levels:
            if level.Id == wall_level_id:
                # Create a sketch plane for the wall's level
                sketch_plane = SketchPlane.Create(doc, level.Id)
                
                # Create a curve array for each wall location curve
                curve_array = CurveArray()
                for curve in curves:
                    curve_array.Append(curve)
                
                # Create the area boundary line from the curve
                # To the view argument pass an area plan view of the respective level
                area_boundary_line = doc.Create.NewAreaBoundaryLine(sketch_plane, curve_array, view)

                # Set the area boundary line's area scheme to the gross area scheme
                if gross_area_scheme is not None:
                    boundary_option = AreaBoundaryOptions()
                    boundary_option.AreaSchemeId = gross_area_scheme.Id
                    doc.Create.NewAreaBoundaryLines(sketch_plane, List[Curve](curve_array), view, boundary_option)

t.Commit() # Don't forget to commit the transaction
