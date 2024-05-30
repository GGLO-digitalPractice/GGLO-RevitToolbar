import clr
import os
import socket
import urllib
import webbrowser
import time
from pyrevit import forms
from pyrevit import script
from Autodesk.Revit.DB import *
from Autodesk.Revit.ApplicationServices import Application

clr.AddReference('System.Management')
from System.Management import ManagementObjectSearcher

def get_revit_file_info():
    doc = __revit__.ActiveUIDocument.Document
    project_file_path = doc.PathName
    project_file_name = os.path.basename(project_file_path)
    
    # Retrieve project information
    project_info = doc.ProjectInformation
    project_number = project_info.Number
    project_name = project_info.Name

    # Retrieve central model file path if it's a workshared model
    central_model_path = ""
    if doc.IsWorkshared:
        central_model_path = ModelPathUtils.ConvertModelPathToUserVisiblePath(doc.GetWorksharingCentralModelPath())
    
    return project_file_name, project_file_path, project_number, project_name, central_model_path

def get_computer_name():
    return socket.gethostname()

def get_user_name():
    return os.environ['USERNAME']

def get_autodesk_id():
    return __revit__.Application.Username

def get_computer_uptime():
    searcher = ManagementObjectSearcher("SELECT LastBootUpTime FROM Win32_OperatingSystem")
    for os in searcher.Get():
        last_boot = os["LastBootUpTime"].split('.')[0]
        last_boot_time = time.strptime(last_boot, "%Y%m%d%H%M%S")
        last_boot_timestamp = time.mktime(last_boot_time)
        uptime_seconds = time.time() - last_boot_timestamp
        uptime_minutes = uptime_seconds / 60  # convert to minutes
        return uptime_minutes

def get_revit_version_info():
    app = __revit__.Application
    revit_version = app.VersionNumber
    revit_build = app.VersionBuild
    return revit_version, revit_build

def get_memory_usage():
    searcher = ManagementObjectSearcher("SELECT TotalVisibleMemorySize, FreePhysicalMemory FROM Win32_OperatingSystem")
    for os in searcher.Get():
        total_memory = float(os["TotalVisibleMemorySize"]) / (1024 ** 2)  # in GB
        free_memory = float(os["FreePhysicalMemory"]) / (1024 ** 2)  # in GB
        return total_memory, free_memory

def get_active_view_name():
    uidoc = __revit__.ActiveUIDocument
    active_view = uidoc.ActiveGraphicalView
    return active_view.Name

def get_file_size(file_path):
    return os.path.getsize(file_path) / (1024 ** 2)  # in MB

def get_c_drive_usage():
    searcher = ManagementObjectSearcher("SELECT Size, FreeSpace FROM Win32_LogicalDisk WHERE DeviceID='C:'")
    for disk in searcher.Get():
        total = float(disk["Size"])
        free = float(disk["FreeSpace"])
        used = total - free
        percent_full = (used / total) * 100
        return percent_full

def create_support_ticket_email(data):
    email_address = "digital-support@gglo.com"  # Updated email address
    subject = "Support Ticket - Revit"
    body = (
        "\n"
        "\n"
        "Team Member, please fill out your issue / need for sending a ticket above.\n"
        "----------------------------------------------\n"
        "Computer Name: {computer_name}\n"
        "User Name: {user_name}\n"
        "Autodesk ID: {autodesk_id}\n"
        "Computer Uptime: {computer_uptime} minutes\n"
        "Active Revit View: {active_view}\n"
        "Project Number: {project_number}\n"
        "Project Name: {project_name}\n"
        "Revit Version: {revit_version}\n"
        "Revit Build: {revit_build}\n"
        "Total Memory: {total_memory} GB\n"
        "Free Memory: {free_memory} GB\n"
        "Revit Local Model File Path: {local_model_path}\n"
        "Revit Central Model File Path: {central_model_path}\n"
        "Local Model File Size: {local_model_size} MB\n"
        "C Drive Usage: {c_drive_usage}%\n"
    ).format(
        computer_name=data["computer_name"],
        user_name=data["user_name"],
        autodesk_id=data["autodesk_id"],
        computer_uptime=data["computer_uptime"],
        active_view=data["active_view"],
        project_number=data["project_number"],
        project_name=data["project_name"],
        revit_version=data["revit_version"],
        revit_build=data["revit_build"],
        total_memory=data["total_memory"],
        free_memory=data["free_memory"],
        local_model_path=data["local_model_path"],
        central_model_path=data["central_model_path"],
        local_model_size=data["local_model_size"],
        c_drive_usage=data["c_drive_usage"]
    )
    
    mailto_link = "mailto:{0}?subject={1}&body={2}".format(
        email_address, urllib.quote(subject), urllib.quote(body)
    )
    webbrowser.open(mailto_link)

def main():
    project_file_name, project_file_path, project_number, project_name, central_model_path = get_revit_file_info()
    computer_name = get_computer_name()
    user_name = get_user_name()
    autodesk_id = get_autodesk_id()
    computer_uptime = "{:.2f}".format(float(get_computer_uptime()))  # format as float
    active_view_name = get_active_view_name()
    revit_version, revit_build = get_revit_version_info()
    total_memory, free_memory = get_memory_usage()
    local_model_size = "{:.2f}".format(float(get_file_size(project_file_path)))  # format as float
    c_drive_usage = "{:.2f}".format(float(get_c_drive_usage()))  # format as float

    data = {
        "computer_name": computer_name,
        "user_name": user_name,
        "autodesk_id": autodesk_id,
        "computer_uptime": computer_uptime,
        "active_view": active_view_name,
        "project_number": project_number,
        "project_name": project_name,
        "revit_version": revit_version,
        "revit_build": revit_build,
        "total_memory": "{:.2f}".format(total_memory),  # format as float
        "free_memory": "{:.2f}".format(free_memory),  # format as float
        "local_model_path": project_file_path,
        "central_model_path": central_model_path,
        "local_model_size": local_model_size,
        "c_drive_usage": c_drive_usage
    }

    create_support_ticket_email(data)

if __name__ == "__main__":
    main()
