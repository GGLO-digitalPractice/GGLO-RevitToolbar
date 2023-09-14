import clr
import os
import math

# Import Revit API
clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import FamilyLoadSettings, Color, FilteredElementCollector, BuiltInCategory, Transaction, ElementId, FamilySymbol, View, TextNoteType, BuiltInParameter, Family, IFamilyLoadOptions, XYZ, Line

# get the current document
doc = __revit__.ActiveUIDocument.Document

# Set up the color
blue = Color(44,128,255)

# Function to convert the color
def CreateINTColor(color):
    return int(color.Red) + int(color.Green) * int(math.pow(2,8)) + int(color.Blue) * int(math.pow(2,16))

intblue = CreateINTColor(blue)

class FamilyOption(IFamilyLoadOptions):
    def OnFamilyFound(self, familyInUse, overwriteParameterValues):
        overwriteParameterValues = True
        return True

    def OnSharedFamilyFound(self, sharedFamily, familyInUse, source, overwriteParameterValues):
        overwriteParameterValues = True
        return True

# Define the base directory
base_dir = r"C:\Temp"

# Find the door tag family symbol
door_tags = FilteredElementCollector(doc).OfClass(FamilySymbol).OfCategory(BuiltInCategory.OST_DoorTags).ToElements()

# For each door tag family
for door_tag in door_tags:
    # Get the family name
    family_name = door_tag.Family.Name

    # Open the family document
    family_doc = doc.EditFamily(door_tag.Family)

    # Collect all TextNoteTypes in the family document
    text_note_types = FilteredElementCollector(family_doc).OfClass(clr.GetClrType(TextNoteType)).ToElements() 

    # Start a transaction
    t = Transaction(family_doc, "Change color of text note type and create a line")
    t.Start()

    try:
        # Change the color of each TextNoteType
        for text_note_type in text_note_types:
            print(text_note_type.get_Parameter(BuiltInParameter.LINE_COLOR).Set(intblue))
            # Access the TEXT_FONT parameter and set it to a new value
            print("Before:", text_note_type.get_Parameter(BuiltInParameter.TEXT_FONT).AsString())
            text_note_type.get_Parameter(BuiltInParameter.TEXT_FONT).Set("Arial")
            print("After:", text_note_type.get_Parameter(BuiltInParameter.TEXT_FONT).AsString())
            
        # Get the first available view
        view = FilteredElementCollector(family_doc).OfClass(View).FirstElement()
        # Define start and end points
        start = XYZ(0, 0, 0)
        end = XYZ(10, 10, 0)
        # Create a new Line
        line = Line.CreateBound(start, end)
        # Create a new DetailCurve
        detailCurve = family_doc.FamilyCreate.NewDetailCurve(view, line)

        # Commit the transaction if successful
        t.Commit()

    except Exception as ex:
        # Roll back the transaction in case of error
        print("Error: ", ex)
        if t.HasStarted():  # Check if the transaction has started before rolling back
            t.RollBack()

    # Proceed with the rest of the code after the try-except block
    # Create a unique file path for the family
    temp_file_path = os.path.join(base_dir, "{}.rfa".format(family_name))

    # Before saving the family document
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path) # This will delete the existing file

    # After saving the family document
    family_doc.SaveAs(temp_file_path)

    # Close the family document
    family_doc.Close(False)
    
     # And when you load the family:
    loadOpts = FamilyOption()
    loadSuccess, familyOut = doc.LoadFamily(temp_file_path, loadOpts)
    family = familyOut

    # Get the FamilySymbol for the loaded family
    familySymbol = family.FamilySymbols.GetEnumerator()
    familySymbol.MoveNext()
    familySymbol = familySymbol.Current

    # Start a transaction to update the instances
    t3 = Transaction(doc, "Update instances")
    t3.Start()

    # Find the instances of the door tag in the document
    instances = FilteredElementCollector(doc).OfClass(FamilyInstance).OfCategory(BuiltInCategory.OST_DoorTags).ToElements()

    # For each instance, set the symbol to the loaded family symbol
    for instance in instances:
        instance.Symbol = familySymbol

    t3.Commit()

# Regenerate the document
t2 = Transaction(doc, "Regenerate document")
t2.Start()
doc.Regenerate()
t2.Commit()
