#! pyhthon3
"""Opens a Revit Model and enables user to select wall types to import"""

__title__ = 'Import Walls'
__author__ = 'Sean Burke, Ren Rainville and MS Copilot'

import clr
import os
import System

# Import RevitAPI
clr.AddReference("RevitAPI")
import Autodesk
from Autodesk.Revit.DB import *

# Import System collections for .NET List
from System.Collections.Generic import List

# Import pyRevit
from pyrevit import revit, DB, forms, script

def filter_wall_types_by_construction_type(wall_types, construction_type):
    # Define wall type prefixes based on construction type
    type_prefixes = {
        "Type I": ["A", "B", "C", "G", "H01", "H02", "H03", "H04", "H05", "H06", "H07", "H08", "H09"],
        "Type III": ["A", "B", "C", "G", "H01", "H02", "H03", "H04", "H05", "H06", "H07", "H08", "H09"],
        "Type IV": ["A", "D", "E", "G", "H20", "H21", "H22", "H23", "H24"],
        "Type V": ["A", "D", "E", "G", "H20", "H21", "H22", "H23", "H24"]
    }
    selected_prefixes = type_prefixes[construction_type]
    return [wall_type for wall_type in wall_types if any(wall_type.LookupParameter("Type Name").AsString().startswith(prefix) for prefix in selected_prefixes)]

def import_wall_types(source_model_path):
    # Set up the transaction
    with revit.Transaction("Import Wall Types"):
        # Open the source model
        source_model = open_document_in_background(source_model_path)
        
        # Collect all wall types in the source model
        collector = FilteredElementCollector(source_model)
        wall_types = collector.OfClass(WallType).ToElements()

        # Offer the user a list of building construction types
        construction_types = ["Type I", "Type III", "Type IV", "Type V"]
        selected_type = forms.ask_for_one_item(construction_types, default="Type I", prompt="Select Building Construction Type")

        # Filter wall types based on selected construction type
        selected_wall_types = filter_wall_types_by_construction_type(wall_types, selected_type)

        # Create a list of ElementId objects from the selected wall types
        element_ids = List[ElementId]()
        for wall_type in selected_wall_types:
            element_ids.Add(wall_type.Id)

        # Copy elements to the current document
        copied_elements = ElementTransformUtils.CopyElements(source_model, element_ids, revit.doc, None, None)

def open_document_in_background(document_path):
    # Convert the string path to a ModelPath
    model_path = ModelPathUtils.ConvertUserVisiblePathToModelPath(document_path)

    # Create OpenOptions object
    open_options = DB.OpenOptions()

    # Open the document in the background using the Revit application
    uiapp = __revit__
    app = uiapp.Application
    background_document = app.OpenDocumentFile(model_path, open_options)
    
    return background_document

if __name__ == "__main__":
    # Show a dialog to the user to select a model
    model_path = "H:\Revit\Support Files\Test\WallAssembliesPull\GGLOAssemblyLibrary.rvt"
    
    # If a model was selected, open it in the background
    if model_path:
        background_document = open_document_in_background(model_path)
        # Print the name of the opened document
        # print("Opened document:", background_document.Title)
        import_wall_types(model_path)
        # Close the document when you're done
        background_document.Close(False)
    else:
        forms.alert("No model selected.")