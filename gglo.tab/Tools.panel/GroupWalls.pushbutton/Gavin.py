# Made by Gavin Crump
# Free for use
# BIM Guru, www.bimguru.com.au

# Boilerplate text
import clr

clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
clr.ImportExtensions(Revit.GeometryConversion)

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager 
from RevitServices.Transactions import TransactionManager 

clr.AddReference("RevitAPI")
import Autodesk 
from Autodesk.Revit.DB import *

# Current doc/app/ui
doc = DocumentManager.Instance.CurrentDBDocument

# Preparing input from dynamo to revit
curves_list = [IN[0]]
view_r      = UnwrapElement(IN[1])

# Start making Transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# Make sketchplane at level of view
level_r = view_r.GenLevel
plane_r = SketchPlane.Create(doc, level_r.Id)

# Make area boundary lines from curves
bounds = []

for curves in curves_list:
	bound = []
	for curve in curves:
		crv = curve.ToRevitType()
		line = doc.Create.NewAreaBoundaryLine(plane_r, crv, view_r)
		bound.append(line.ToDSType(True))
	bounds.append(bound)
		
# Finish making transaction
TransactionManager.Instance.TransactionTaskDone()

# Preparing output to Dynamo
OUT = bounds