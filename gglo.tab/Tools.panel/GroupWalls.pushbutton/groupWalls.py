# import required modules
from collections import defaultdict
from pyrevit import revit, DB

# create a FilteredElementCollector to collect all Wall elements
wall_collector = DB.FilteredElementCollector(revit.doc).OfClass(DB.Wall)

# create a defaultdict to hold the groups
grouped_walls = defaultdict(lambda: defaultdict(list))

# iterate over the wall_collector
for wall in wall_collector:
    # get the wall level
    wall_level = revit.doc.GetElement(wall.LevelId).Name

    # get the wall function
    wall_function = wall.WallType.Function

    # add the wall to the group
    grouped_walls[wall_level][wall_function].append(wall.Id)

# print out the grouped walls
for level, functions in grouped_walls.items():
    print("Level: %s" % level)
    for function, walls in functions.items():
        print("  Function: %s" % function)
        for wall_id in walls:
            print("    Wall ID: %s" % wall_id)
