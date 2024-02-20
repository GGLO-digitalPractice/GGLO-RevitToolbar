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
    # ***if we want all groups in the project, including those not placed***
    # ***we need to change to GroupType in .OfClass(GroupType)***
    # all_groups = DB.FilteredElementCollector(revit.doc).OfClass(DB.GroupType).ToElements()
    all_groups = DB.FilteredElementCollector(revit.doc).OfClass(DB.Group).ToElements()
    # Display in a selectable list
    selected_groups = forms.SelectFromList.show([g.Name for g in all_groups], multiselect=True)
    return selected_groups

# Check if Project Info has Client Name and Project Name, if either is null / empty ask for info
def set_project_info():
    project_info = DB.FilteredElementCollector(revit.doc).OfClass(DB.ProjectInfo).FirstElement()
    if project_info is not None:
        # Access the Name porperty
        pi_proj_name = project_info.Name
        pi_client_name = project_info.ClientName

    if pi_client_name == None or pi_client_name == "ENTER CLIENT NAME":
        client_name = forms.ask_for_unique_string("Please provide Client Abbreviation", default = str(pi_client_name), title = "Client Abbreviation")
    else:
        client_name = forms.ask_for_unique_string("Accept or Correct Client Abbreviation", default = str(pi_client_name), title = "Accept or Correct Client Abbreviation")
    if pi_proj_name == None or pi_proj_name == "PROJECT NAME":
        proj_name = forms.ask_for_unique_string("Please provide Project Name", default = str(pi_proj_name), title = "Project Name")
    else:
        proj_name = forms.ask_for_unique_string("Accept or Correct Project Name", default = str(pi_proj_name), title = "Accept or Correct Project Name")
    path_prefix = client_name.replace(" ", "") + "_" + proj_name.replace(" ", "") + "_"
    return path_prefix

# *** Need to find a specific location for where this file lives for the

UnitGroupSrc = "H:/Grasshopper/04 - RhinoInsideTools/_WIP/07_Unit Groups to Rhino\UnitGroup.rvt"
# Eventually will want to set a specific output folder, possibly note that and show to the user for confirmation purposes
# UnitGroupDest = 'H:\Grasshopper\04 - RhinoInsideTools\_WIP\07_Unit Groups to Rhino\SeparateUnitGroups\'

# define function to save group as revit model

def save_groups_as_rvt(selected_groups, folder_path, path_prefix):
    orig_doc = revit.doc
    orig_ui_doc = revit.uidoc

    for group_name in selected_groups:
        # Find the group by name
        group = next((g for g in DB.FilteredElementCollector(revit.doc).OfClass(DB.Group) if g.Name == group_name), None)
        if group is None:
            continue

        # Create a new Revit document
        # ui_doc = uiapp.OpenAndActivateDocument(UnitGroupSrc)
        new_doc = uiapp.OpenAndActivateDocument(UnitGroupSrc).Document
        old_doc = new_doc

        # Start a transaction to modify the new document
        with DB.Transaction(new_doc, 'Copy Group') as trans:
            trans.Start()

            # Copy the group to the new document
            copied_group = DB.ElementTransformUtils.CopyElements(orig_doc, List[DB.ElementId]([group.Id]), new_doc, None, DB.CopyPasteOptions())
            trans.Commit()

        # Save the new document
        save_path = os.path.join(folder_path, path_prefix + group_name + ".rvt")

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
            old_doc.Close(False)

# Select Folder Path
# will only need this for testing
# will provide a static collection folder that team members cannot change

def select_folder():
    folder_path = forms.pick_folder()
    if not folder_path:
        forms.alert('No folder selected.', exitscript=True)
    return folder_path


# Main Script Execution

selected_groups = select_model_groups()
path_prefix = set_project_info()
if selected_groups:
    folder_path = forms.pick_folder()
    if folder_path:
        save_groups_as_rvt(selected_groups, folder_path, path_prefix)
