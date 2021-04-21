import arcade
import math
import numpy as np
import matplotlib.pyplot as mp
frames_per_update = 3
left = 1
right = 0
from physics import Geometry
pg = Geometry()
# THROWING KNIFE
class ThrowingKnife(arcade.Sprite):
    def __init__(self, parent):
        super().__init__("resources/sprites/4x/dagger4x.png", .4)
        self.parent = parent
        self.direction = self.parent.direction
        self.attacked = True
        self.thrown = False
        self.range = 5
        self.target_x, self.target_y = 0, 0
        self.path = []

    def update(self):
        # update the position and direction while not attacking
        self.direction = self.parent.direction
        # print(f"target_x: {self.target_x} current_x: {self.center_x}")
        if self.thrown:
            if self.path:
                self.center_y = self.path[0][1]
                self.center_x = self.path[0][0]
                self.path.pop(0)
            else:
                self.thrown = False

    def attack(self, x, y):
        print(f"player (x, y): ({self.parent.center_x, self.parent.center_y})")
        print(f"target (x, y): ({x, y})")
        # move the dagger in sync with the players movement
        self.target_x, self.target_y = x, y
        self.set_direction(self.direction)
        self.path = pg.calc_para((self.target_x, self.target_y), 200, cutoff=-50, show=False, output=True, x_trans=1/500, precision=.25)
        # self.path = self.calc_para((self.target_x, self.target_y))
        # self.change_y = 2
        self.thrown = True

    def set_direction(self, direction):
        if direction == right:
            self.change_x = 8
            # self.angle = -45
            self.center_x = self.parent.right
            self.center_y = self.parent.center_y - 14
        elif direction == left:
            self.change_x = -8
            # self.angle = 90 + 45
            self.center_x = self.parent.left
            self.center_y = self.parent.center_y - 10

    def calc_para(self, vertex: tuple):
        range = self.range * 64
        min_y = self.parent.center_y - 32
        h, k = vertex
        diff = h - self.parent.center_x
        # print("diff", diff)
        if diff > 200:
            print(f"h_before{h}")
            nr = (diff - 350)
            h = self.parent.center_x + 150
            k += 100
            print(f"h_after{h}")
        elif diff < 38:
            print(f"diff: {diff}")
            h = self.parent.center_x + 50

        a = -1/50
        x = np.linspace(self.parent.center_x, h + range, 100)
        # y = -x**2
        y = a * (x - h) ** 2 + k
        points = [(xp, yp) for xp, yp in zip(x, y) if yp >= min_y]
        return points



    def triangulate(self, point: tuple):
        x, y = point
        opp = x - self.parent.center_y
        adj = y - self.parent.center_x



















class Slash(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("resources/sprites/dagger_slash/0.png", scale=.5)
        self.center_x, self.center_y = x, y
        self.path = "resources/sprites/dagger_slash/"
        self.animation_length = 4
        self.animation_speed = 5
        self.textures = [arcade.load_texture_pair(f"{self.path}{x}.png") for x in range(self.animation_length)]
        self.cur_texture_index = 0
        self.frame = 0
        self.complete = False
        self.direction = 0

    def update_animation(self, delta_time: float = 1/60):
        self.frame += 1
        if self.frame >= frames_per_update * self.animation_length:
            print("complete")
            self.frame = 0
            self.complete = True

        # print(f"frame:{self.frame}")
        self.cur_texture_index = self.frame // frames_per_update
        # print(self.cur_texture_index)
        self.texture = self.textures[self.cur_texture_index][self.direction]
        if self.cur_texture_index > self.animation_length -1:
            self.cur_texture_index = 0

    def is_complete(self):
        return self.complete






