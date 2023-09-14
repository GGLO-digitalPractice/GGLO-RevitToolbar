#script_utils.py
# Import relevant libraries
import clr
import math

# Import Revit API
clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import Category, Color, Transaction, CategoryType, DimensionType, GridType, LevelType, FilteredElementCollector, TextNoteType, BuiltInCategory, BuiltInParameter, GraphicsStyleType

def change_color_of_categories(doc, search_terms_colors):
    """
    Changes color of categories.
    doc: The document in which to change the categories' color
    search_terms_colors: A list of tuples/lists. Each tuple/list contains search terms and corresponding color.
    """
    # Get all annotation categories
    categories = doc.Settings.Categories

    for search_terms, color in search_terms_colors:
        # Filter categories based on search terms
        annotation_categories = [c for c in categories 
                                 if c.CategoryType == CategoryType.Annotation 
                                 and any(term in c.Name for term in search_terms)]
        
        # Change color of the filtered categories
        for category in annotation_categories:
            gstyle = category.GetGraphicsStyle(GraphicsStyleType.Projection)
            if gstyle is not None:
                gstyle.GraphicsStyleCategory.LineColor = color
def get_text_note_name(text_note):
    # Try getting the name from the SYMBOL_NAME_PARAM parameter
    param = text_note.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM)
    if param:
        return param.AsString()
    return None

def change_color_of_types(doc, color):
    # Get all DimensionType, GridType, LevelType, and TextNoteType elements in the document
    dimension_types = FilteredElementCollector(doc).OfClass(DimensionType).ToElements()
    grid_types = FilteredElementCollector(doc).OfClass(GridType).ToElements()
    level_types = FilteredElementCollector(doc).OfClass(LevelType).ToElements()
    text_note_types = [
        tnt for tnt in FilteredElementCollector(doc).OfClass(TextNoteType).ToElements()
        if tnt and "working" not in get_text_note_name(tnt).lower() and "redline" not in get_text_note_name(tnt).lower()
    ]   
    # Convert Color to integer value used in Revit
    int_color = CreateINTColor(color)

    all_types = []
    all_types.extend(dimension_types)
    all_types.extend(level_types)
    all_types.extend(text_note_types)  # Add text note types to the list

    # Iterate over all types and set the LineColor to the provided color
    for element_type in all_types:
        # Check if the type has 'LINE_COLOR' parameter
        if element_type.get_Parameter(BuiltInParameter.LINE_COLOR) is not None:
            element_type.get_Parameter(BuiltInParameter.LINE_COLOR).Set(int_color)
    
    for grid_type in grid_types:
        # Check if the type has 'GRID_END_SEGMENT_COLOR' parameter
        if grid_type.get_Parameter(BuiltInParameter.GRID_END_SEGMENT_COLOR) is not None:
            grid_type.get_Parameter(BuiltInParameter.GRID_END_SEGMENT_COLOR).Set(int_color)



def CreateINTColor(color):
    return int(color.Red) + int(color.Green) * int(math.pow(2,8)) + int(color.Blue) * int(math.pow(2,16))   