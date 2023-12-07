#! pyhthon3

"""Print the full path to the central model (if model is workshared).

Shift+Click:
Open central model path in file browser
"""
# import common libraries
import clr
import os
import shutil

# import Revit libraries
from pyrevit import script
from pyrevit import forms
from Autodesk.Revit.UI.Selection import *

# Get the current document
doc = __revit__.ActiveUIDocument.Document

if forms.check_workshared(doc=doc):
    central_path = doc.GetWorksharingCentralModelPath()
    if script.get_shift_key_state():
        os.system('explorer /select, "{}"'.format(central_path))
    else:
        print(central_path)

