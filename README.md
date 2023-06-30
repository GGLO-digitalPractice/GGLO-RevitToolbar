# GGLO-Toolbar

The GGLO Toolbar is a pyRevit extension, and is built on the WIP version 4.8.13, which is compatible up to Revit 2024.
https://github.com/eirannejad/pyRevit

Many thanks to the Aussi BIM Guru for the guRoo sample extension, of which some of the tools are based.
https://github.com/aussieBIMguru/guRoo

The following method can be used to avoid installing pyRevit via the Settings menu from within Revit itself, and might be beneficial to automate company related installation process' as well.

# Directly installing the GGLO-Toolbar
Install pyRevit from https://github.com/eirannejad/pyRevit/releases
WIN+R, then type 'cmd'
In the command line, install the extension with the following command:
*****************
pyrevit extend ui GGLO-Toolbar https://github.com/GGLO-digitalPractice/GGLO-RevitToolbar.git --dest="C:\\_GGLO\RevitTools" --branch=main
***************** 
  If Revit was opened, use the reload button of pyRevit
