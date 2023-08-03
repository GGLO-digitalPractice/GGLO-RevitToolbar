import json

def load_data_from_file(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data

def transform_data(data):
    titles = []
    for item in data["omniclass"]["level1"]:
        title = item["_title"]
        titles.append(title)
    return titles

data = load_data_from_file('C:\_GGLO\RevitTools\GGLO-Toolbar.extension\gglo.tab\Rooms.panel\OmniClass.pushbutton\OmniClass13-Level1.json')
transformed_data = transform_data(data)
print(transformed_data)
