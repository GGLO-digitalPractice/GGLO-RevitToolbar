# Import relevant libraries
import clr

# Import Revit API
clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import Category, Color, Transaction, CategoryType, DimensionType, GridType, LevelType, FilteredElementCollector, BuiltInCategory, BuiltInParameter

# Define your functions here

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
        annotation_categories = [c for c in categories if c.CategoryType == CategoryType.Annotation and any(term in c.Name for term in search_terms)]
        
        # Change color of the filtered categories
        for category in annotation_categories:
            category.LineColor = color


def change_color_of_types(doc, color):
    # Get all DimensionType, GridType, and LevelType elements in the document
    dimension_types = list(FilteredElementCollector(doc).OfClass(clr.GetClrType(DimensionType)))
    grid_types = list(FilteredElementCollector(doc).OfClass(clr.GetClrType(GridType)))
    level_types = list(FilteredElementCollector(doc).OfClass(clr.GetClrType(LevelType)))
    
    all_types = dimension_types + grid_types + level_types

    # Iterate over all types and set the LineColor to the provided color
    for element_type in all_types:
        if isinstance(element_type, DimensionType):
            line_style = element_type.LineStyle
            if line_style is not None and line_style.GraphicsStyleCategory is not None:
                line_style.GraphicsStyleCategory.LineColor = color

