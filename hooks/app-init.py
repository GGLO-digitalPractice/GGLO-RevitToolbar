# import pyrevit libraries
import clr
from pyrevit import forms,script
from guRoo_msgUtils import *

# check if notifications are disabled
if msgUtils_muted():
	script.exit()

# Get icon file (doesn't work)
# curPath = script.get_script_path()
# remPath = curPath.split('gglo.tab')[0]
# icoFile = remPath + r'bin\Graphics\gglo.ico'

# Display the message to the user
forms.toast("Toolbar has been loaded!","GGLO Tools for Revit",appid="GGLO Tools",actions={"GGLO Digital":"https://www.gglo.com"})
