import json

# set the correct paths for resources
texture_path = "resources/sprites/item/"
sound_path = "resources/sounds/"
file_path = "config/items.json"

# load the file containing all items and their properties
with open(file_path) as itms:
    items = json.load(itms)

# get only the items which are knives
knives = items['knives']


# load a knife object when given a dictionary
def load_knife(knife_name):
    if knife_name in list(knives.keys()):
        item = Knife(knives[knife_name])
        item.name = knife_name
        return item


# abstract item class
class Item:
    def __init__(self):
        self.name = None
        self.texture = None
        self.scale = None


# Knife object loaded from provided item dictionary
class Knife(Item):
    def __init__(self, knife_object):
        super(Knife, self).__init__()
        # load instance variables set to the values in the loaded dictionary for the knife
        self.texture = f"{texture_path}{knife_object['texture']}"
        self.sounds = [f"{sound_path}{knife_object['sound']}{i}.wav" for i in range(3)]
        self.scale = knife_object['scale']
        stats = knife_object['stats']
        self.speed = stats['velocity']
        self.range = stats['range']
        self.max_speed = stats['max_velocity']


