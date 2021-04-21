import arcade

class Grass(arcade.Sprite):
    def __init__(self, x, y, scale):
        super().__init__("resources/sprites/4x/grass4X.png", center_x=x, center_y=y, scale=scale)

    def update(self):
        pass

class Terrain:
    def __init__(self, level_map):
        self.terrain_map = level_map
    def load_map(self):
        # for each in
        pass

    def generate(self):
        pass

