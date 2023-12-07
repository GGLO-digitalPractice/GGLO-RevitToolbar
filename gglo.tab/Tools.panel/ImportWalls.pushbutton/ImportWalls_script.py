#! pyhthon3
"""Opens a Revit Model and enables user to select wall types to import"""

__title__ = 'Import Walls'
__author__ = 'Sean Burke'

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

def open_document_in_background(document_path):
    # Convert the string path to a ModelPath
    model_path = ModelPathUtils.ConvertUserVisiblePathToModelPath(document_path)

    # Create OpenOptions object
    open_options = DB.OpenOptions()

    # Open the document in the background
    background_document = revit.Application.Application.OpenDocumentFile(model_path, open_options)
    
    return background_document

def import_wall_types(source_model_path):
    # Set up the transaction
    with revit.Transaction("Import Wall Types"):
        # Open the source model
        source_model = revit.Application.Application.OpenDocumentFile(source_model_path)
        
        # Collect all wall types in the source model
        collector = FilteredElementCollector(source_model)
        wall_types = collector.OfClass(WallType).ToElements()

        # Copy elements to the current document
        copied_elements = ElementTransformUtils.CopyElements(source_model, List[ElementId](wall_type.Id for wall_type in wall_types), revit.doc, None, None)

if __name__ == "__main__":
    # Show a dialog to the user to select a model
    model_path = forms.pick_file(file_ext='rvt')
    
    # If a model was selected, open it in the background
    if model_path:
        background_document = open_document_in_background(model_path)
        # Do something with the background document here...
        # Print the name of the opened document
        print("Opened document:", background_document.Title)
        trans_walls = import_wall_types(model_path)
        # Don't forget to close the document when you're done:
        background_document.Close(False)
    else:
        forms.alert("No model selected.")

