"""Print the full path to the central model (if model is workshared).

Shift+Click:
Open central model path in file browser
"""
#pylint: disable=E0401,invalid-name
# import libraries
import clr
import os.path as op
import shutil
# import pyrevit libraries
from pyrevit import forms
from pyrevit import revit, DB
from pyrevit import script
from Autodesk.Revit.UI.Selection import *

# Get the current document
doc = __revit__.ActiveUIDocument.Document

if forms.check_workshared(doc=revit.doc):
    central_path = revit.query.get_central_path(doc=revit.doc)
    if __shiftclick__:  #pylint: disable=E0602
        script.show_folder_in_explorer(op.dirname(central_path))
    else:
        print(central_path)

