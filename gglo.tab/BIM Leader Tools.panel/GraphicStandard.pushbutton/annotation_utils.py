#annotation_utils.py
import os
import tempfile
import clr
import traceback
import math
from pyrevit import forms
import logging

# Import Revit API
clr.AddReference("RevitAPI")
import Autodesk.Revit.UI as RevitUI
import Autodesk.Revit.DB as RevitDB

from Autodesk.Revit.DB import (IFamilyLoadOptions, Category, Transaction, CategoryType, DimensionType, GridType, LevelType, 
                               FilteredElementCollector, TextNoteType, BuiltInCategory, BuiltInParameter, GraphicsStyleType, Family)

# Import System.Drawing for fonts
clr.AddReference("System.Drawing")
import System.Drawing as SysDrawing
from System.Drawing import Text, Color

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
active_doc = __revit__.ActiveUIDocument.Document

import Autodesk.Revit.DB as RevitDB
import Autodesk.Revit.UI as RevitUI
from Autodesk.Revit.DB import Transaction, FilteredElementCollector

class FamilyLoadOptions(IFamilyLoadOptions):
    def OnFamilyFound(self, familyInUse, overwriteParameterValues):
        overwriteParameterValues = True
        return True

    def OnSharedFamilyFound(self, sharedFamily, familyInUse, source, overwriteParameterValues):
        overwriteParameterValues = True
        return True

def process_family_from_object(doc, family, action):
    """
    Open a family from a Family instance, perform an action, and reload it back into the project.

    :param doc: Active document.
    :param family: Family instance.
    :param action: Function to perform on the family.
    :return: None.
    """
    
    # Check if family is editable
    if not family.IsEditable:
        print("Family {} is not editable.".format(family.Name))
        return

    # Open family document
    family_doc = doc.EditFamily(family)
    print(family_doc)
    # Perform action on the family
    action(family_doc)

    # Save the family document to a temporary location
    original_name = family.Name.replace(" ", "_")  # Replacing spaces to ensure a valid filename
    temp_file = os.path.join(tempfile.gettempdir(), original_name + "_temp.rfa")
    print temp_file
    family_doc.SaveAs(temp_file)
    family_doc.Close(False)  # Close without saving changes again

    # Reload the family into the project, ensuring the old reference is not used.
    if not doc.LoadFamily(temp_file):
        print("Error loading family")

    # Optional: Remove the temporary file after loading the family
    # os.remove(temp_file)


# Example usage:

def modify_family_font_and_color(family_doc, chosen_font, chosen_color):
    """Modify a family document's text style font and color."""
    
    with Transaction(family_doc, "Modify Font and Color") as t:
        t.Start()
        # Update the font for all text note types and dimension types
        print("Modifying family colors:")
        change_color_of_family_types(family_doc, chosen_color)  # Use the primary color
        print("Modifying family fonts:")
        if chosen_font:
            modify_family_font(chosen_font, family_doc)
        t.Commit()
        
def modify_family_font(chosen_font, family_doc):
    text_note_types = FilteredElementCollector(family_doc).OfClass(TextNoteType).ToElements()
    for text_note_type in text_note_types:
        param = text_note_type.get_Parameter(BuiltInParameter.TEXT_FONT)
        if param:
            param.Set(chosen_font)
            print(text_note_type, chosen_font)
            
def change_color_of_family_types(family_doc, color):
    exclusion_keywords = ["working", "redline"]
    text_note_types = filter_elements_by_type_and_name(TextNoteType, exclusion_keywords)

    for text_note_type in text_note_types:
        if text_note_type.get_Parameter(BuiltInParameter.LINE_COLOR) is not None:
            text_note_type.get_Parameter(BuiltInParameter.LINE_COLOR).Set(color)

def system_color_to_rgb(system_color_value):
    color_system = SysDrawing.Color.FromArgb(system_color_value)
    return color_system.R, color_system.G, color_system.B

def modify_font(chosen_font, doc):
    text_note_types = FilteredElementCollector(doc).OfClass(TextNoteType).ToElements()
    dimension_types = FilteredElementCollector(doc).OfClass(DimensionType).ToElements()

    all_types = list(text_note_types)
    all_types.extend(list(dimension_types))

    for element_type in all_types:
        param = element_type.get_Parameter(BuiltInParameter.TEXT_FONT)
        if param:
            param.Set(chosen_font)
            print(element_type, chosen_font)

def color_setup(color_system):
    r, g, b = system_color_to_rgb(color_system)
    color_revit = RevitDB.Color(r, g, b)
    red = RevitDB.Color(128,0,0)
    npb = RevitDB.Color(164, 221, 237)

    search_terms_colors = [
        (["Tag", "View", "Grid", "Symbol", "Section Line", "Mark", "Annotation", "Stair", "Matchline", "Head", "Callout"], color_revit),
        (["Revision"], red),
        (["Guide Grid", "Reference", "Boxes", "Plan Region"], npb)
    ]
    return search_terms_colors

# ---------- font_utils Functions ----------
chosen_font = None

def ask_for_font():
    global chosen_font

    installed_fonts = Text.InstalledFontCollection().Families
    available_fonts = [font.Name for font in installed_fonts if hasattr(font, 'Name')]
    selected_font = forms.SelectFromList.show(available_fonts, 
                                              title="Select a Font", 
                                              subtitle="Note: Not all installed fonts listed are compatible with Revit.")
    
    if selected_font:
        chosen_font = selected_font if isinstance(selected_font, str) else selected_font[0]
    return chosen_font

# ---------- script_utils Functions ----------
def get_annotation_families_from_categories(doc, matching_categories):
    # Using a set to store unique families (since families might be repeated across categories)
    annotation_families = set()

    # Collect all families in the document
    collector = FilteredElementCollector(doc).OfClass(RevitDB.Family)

    for family in collector:
        # Check if the family is of annotation type and belongs to one of the matching categories
        if family.FamilyCategory and family.FamilyCategory.Name in matching_categories:
            annotation_families.add(family.Name)

    return list(annotation_families)


def get_annotation_categories(doc, search_terms_colors):
    """Retrieve annotation categories based on search terms."""
    categories = doc.Settings.Categories
    all_annotation_categories = []

    for search_terms, _ in search_terms_colors:
        annotation_categories = [c for c in categories 
                                 if c.CategoryType == CategoryType.Annotation 
                                 and any(term in c.Name for term in search_terms)]
        all_annotation_categories.extend(annotation_categories)

    return all_annotation_categories

def change_color_of_categories(annotation_categories, search_terms_colors):
    """Change the color of the retrieved annotation categories."""
    for search_terms, color in search_terms_colors:
        matching_categories = [c for c in annotation_categories 
                               if any(term in c.Name for term in search_terms)]
        
        for category in matching_categories:
            gstyle = category.GetGraphicsStyle(GraphicsStyleType.Projection)
            if gstyle is not None:
                gstyle.GraphicsStyleCategory.LineColor = color

def get_type_name(types):
    param = types.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM)
    if param:
        return param.AsString()
    return None
    
def filter_elements_by_type_and_name(element_type, exclusion_keywords):
    return [
        elem for elem in FilteredElementCollector(doc).OfClass(element_type).ToElements()
        if elem and all(keyword not in get_type_name(elem).lower() for keyword in exclusion_keywords)
    ]
def change_color_of_types(doc, color):
    grid_types = FilteredElementCollector(doc).OfClass(GridType).ToElements()
    level_types = FilteredElementCollector(doc).OfClass(LevelType).ToElements()
    exclusion_keywords = ["working", "redline"]
    text_note_types = filter_elements_by_type_and_name(TextNoteType, exclusion_keywords)
    dimension_types = filter_elements_by_type_and_name(DimensionType, exclusion_keywords)
    
    int_color = CreateINTColor(color)

    all_types = []
    all_types.extend(dimension_types)
    all_types.extend(level_types)
    all_types.extend(text_note_types)

    for element_type in all_types:
        if element_type.get_Parameter(BuiltInParameter.LINE_COLOR) is not None:
            element_type.get_Parameter(BuiltInParameter.LINE_COLOR).Set(int_color)
    
    for grid_type in grid_types:
        if grid_type.get_Parameter(BuiltInParameter.GRID_END_SEGMENT_COLOR) is not None:
            grid_type.get_Parameter(BuiltInParameter.GRID_END_SEGMENT_COLOR).Set(int_color)

def CreateINTColor(color):
    return int(color.Red) + int(color.Green) * int(math.pow(2,8)) + int(color.Blue) * int(math.pow(2,16))

# MAIN Execution
def run_object_styles(chosen_font, chosen_color):
    search_terms_colors = color_setup(chosen_color)
    t = Transaction(doc, "Change color and font of annotations")
    t.Start()
    logging.basicConfig(filename='C:/Users/sean/OneDrive/Documents/GitHub/GGLO-Toolbar.extension/gglo.tab/BIM Leader Tools.panel/GraphicStandard.pushbutton/error.log', level=logging.ERROR) 
    try:
        # Retrieve the annotation categories based on search terms
        annotation_cats = get_annotation_categories(doc, search_terms_colors)
        # Change the color of the retrieved annotation categories
        change_color_of_categories(annotation_cats, search_terms_colors)
        change_color_of_types(doc, search_terms_colors[0][1])  # Use the primary color

        if chosen_font:
            modify_font(chosen_font, doc)

        # t.Commit()
        forms.alert("Annotation Categories' colors and fonts have been successfully updated", title='Success', ok=True)
        uidoc.RefreshActiveView()
    except Exception as e:
        print("Exception occurred:", e)
        traceback.print_exc()
        logging.error(str(e))
        # t.RollBack()
    finally:
        t.Commit()
        
# # FAMILY Execution
# def run_edit_families(chosen_color):            
    # search_terms_colors = color_setup(chosen_color)
    # # Retrieve the annotation categories based on search terms
    # annotation_cats = get_annotation_categories(doc, search_terms_colors)
    
    # first_search_terms, _ = search_terms_colors[0]  # Unpack the first tuple
    # first_matching_categories = [c.Name for c in annotation_cats 
                                 # if c.CategoryType == CategoryType.Annotation 
                                 # and any(term in c.Name for term in first_search_terms)]
    # # Get annotation families for the matching categories
    # named_families = get_annotation_families_from_categories(doc, first_matching_categories)
    # # Collect all families in the document
    # all_families = FilteredElementCollector(doc).OfClass(Family).ToElements()
    # # Filter the families based on the given names
    # families_from_names = [fam for fam in all_families if fam.Name in named_families]
    
    # for family in families_from_names:
        # process_family_from_object(doc, family, lambda fam_doc: modify_family_font_and_color(fam_doc, chosen_font, chosen_color))

    # t = Transaction(doc, "Change Family Labels and Colors")
    # t.Start()
    # try:
        # # Put the operations here that are supposed to be in the transaction block
        # t.Commit()
    # except Exception as e:
        # print("Exception occurred:", e)
        # traceback.print_exc()
        # t.RollBack()

def select_single_family():
    """Prompt user to select a single family for testing."""
    all_families = FilteredElementCollector(doc).OfClass(Family).ToElements()
    family_names = [f.Name for f in all_families]
    selected_name = forms.SelectFromList.show(family_names, 
                                              title="Select a Family for Testing", 
                                              subtitle="Choose a family to process:")
    if selected_name:
        return next((fam for fam in all_families if fam.Name == selected_name), None)
    return None

def run_test_single_family(chosen_color):
    family = select_single_family()
    if family:
        print("Testing...")
        process_family_from_object(doc, family, lambda fam_doc: modify_family_font_and_color(fam_doc, chosen_font, chosen_color))
    else:
        print("No family selected for testing.")