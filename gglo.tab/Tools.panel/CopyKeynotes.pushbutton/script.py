"""Print the full path to the central model (if model is workshared).

Shift+Click:
Open central model path in file browser
"""
#pylint: disable=E0401,invalid-name
# import libraries
import clr
clr.AddReference('RevitAPI')
import os.path as op
import shutil
# import pyrevit libraries
from pyrevit import forms
from pyrevit import revit, DB
from pyrevit import script
from Autodesk.Revit.UI.Selection import *
from Autodesk.Revit.DB import Document, FilteredElementCollector, BuiltInCategory, BuiltInParameter

# Get the current document
doc = __revit__.ActiveUIDocument.Document

# Retrieve the project information
collector = FilteredElementCollector(doc)
project_info = collector.OfCategory(BuiltInCategory.OST_ProjectInformation).FirstElement()

# Get the project name
project_name = project_info.get_Parameter(BuiltInParameter.PROJECT_NAME).AsString()


if project_name == "PROJECT NAME":
    forms.alert("Project name = 'PROJECT NAME'. \nPlease edit in Project Info. \n\nExiting the command.")
    script.exit()
    
if forms.check_workshared(doc=revit.doc):
    central_path = revit.query.get_central_path(doc=revit.doc)
    # Extract the directory path without the file name
    directory_path = (op.dirname(central_path))
    if __shiftclick__:  #pylint: disable=E0602
        script.show_folder_in_explorer(op.dirname(central_path))
    else:
        sourceFile = "H:/Revit/Support Files/RevitKeynotes_Imperial_GGLO_2023.txt"
        destinationFile = directory_path + "\\" + project_name + "_KeynotesFile.txt"
        file_path = "path/to/file.txt"  # Path to the file that already exists
        if forms.alert("File already exists!", "A file already exists at the specified location and you will lose project specific edits if you proceed. Do you want to overwrite it?",
                       ok=True, cancel=True) == forms.DialogResult.OK:
            # User selected "OK" to overwrite the file
            # Perform the necessary action here (e.g., overwrite the file)
            forms.alert("File replaced successfully with GGLO office master!")
        else:
            # User selected "Cancel" or closed the dialog
            forms.alert("File overwrite canceled.")
            shutil.copy(sourceFile, destinationFile)