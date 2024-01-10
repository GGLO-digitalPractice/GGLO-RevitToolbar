# Import required libraries
from pyrevit import revit, DB
from pyrevit import forms
import os
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from System.Collections.Generic import List
# import shutil

uiapp = __revit__
app = uiapp.Application
# doc = uidoc.Document

# select model groups
def select_model_groups():
    # Get all model groups
    all_groups = DB.FilteredElementCollector(revit.doc).OfClass(DB.Group).ToElements()
    # Display in a selectable list
    selected_groups = forms.SelectFromList.show([g.Name for g in all_groups], multiselect=True)
    return selected_groups

UnitGroupSrc = "H:/Grasshopper/04 - RhinoInsideTools/_WIP/07_Unit Groups to Rhino\UnitGroup.rvt"
# UnitGroupDest = 'H:\Grasshopper\04 - RhinoInsideTools\_WIP\07_Unit Groups to Rhino\SeparateUnitGroups\'

# define function to save group as revit model

#from Autodesk.Revit.DB import Transaction, ElementId, WorksetConfiguration, WorksharingSaveAsOptions, SaveAsOptions

def save_groups_as_rvt(selected_groups, folder_path):
    orig_doc = revit.doc
    orig_ui_doc = revit.uidoc

    for group_name in selected_groups:
        # Find the group by name
        group = next((g for g in DB.FilteredElementCollector(revit.doc).OfClass(DB.Group) if g.Name == group_name), None)
        if group is None:
            continue

        # Create a new Revit document
        ui_doc = uiapp.OpenAndActivateDocument(UnitGroupSrc)
        new_doc = ui_doc.Document

        # Start a transaction to modify the new document
        with DB.Transaction(new_doc, 'Copy Group') as trans:
            trans.Start()

            # Copy the group to the new document
            copied_group = DB.ElementTransformUtils.CopyElements(orig_doc, List[DB.ElementId]([group.Id]), new_doc, None, DB.CopyPasteOptions())
            trans.Commit()

        # Save the new document
        save_path = os.path.join(folder_path, group_name+".rvt")

        if os.path.exists(save_path):
            print("File already exists: " + save_path)
            continue
        else:
            # worksharing_options = DB.WorksharingSaveAsOptions()
            # worksharing_options.SaveAsCentral = True
            save_options = DB.SaveAsOptions()
            # save_options.SetWorksharingOptions(worksharing_options)
            save_options.Compact = True
            save_options.MaximumBackups = 1
            new_doc.SaveAs(save_path, save_options)

        # After processing group, reactivate the original document
        orig_ui_doc = uiapp.OpenAndActivateDocument(orig_ui_doc.Document.PathName)

        # Close the new document
        if new_doc.IsModifiable:
            new_doc.Close(False)

# Select Folder Path
def select_folder():
    folder_path = forms.pick_folder()
    if not folder_path:
        forms.alert('No folder selected.', exitscript=True)
    return folder_path


# Main Script Execution
selected_groups = select_model_groups()
if selected_groups:
    folder_path = forms.pick_folder()
    if folder_path:
        save_groups_as_rvt(selected_groups, folder_path)

# Need to look into checking file's Project Info parameters, to add the Client Abbreviation 
# and Project Name with White Space removed, add that to the group name for path to saveas
# this initial testing was in the Test-ML.rvt file so the unit groups were already named