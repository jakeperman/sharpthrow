import arcade
import math
import numpy as np
import copy
import matplotlib.pyplot as mp
frames_per_update = 3
left = 1
right = 0
from physics import Geometry
import physics
pg = Geometry()
# THROWING KNIFE
class ThrowingKnife(arcade.Sprite):
    def __init__(self, parent):
        super().__init__("resources/sprites/item/knife.png", .5)
        self.parent = parent
        self.direction = self.parent.direction
        self.attacked = True
        self.thrown = False
        self.range = 5
        self.target_x, self.target_y = 0, 0
        self.path = []

    def update(self):
        # update the position and direction while not attacking
        # print(f"target_x: {self.target_x} current_x: {self.center_x}")
        if self.thrown:
            if self.path:
                self.center_y = self.path[0][1]
                self.center_x = self.path[0][0]
                self.path.pop(0)
                if self.direction is right:
                    self.angle -= self.ang_change
                elif self.direction is left:
                    self.angle += self.ang_change
            else:
                self.thrown = False

    def attack(self, x, y):
        print(f"player (x, y): ({self.parent.center_x, self.parent.center_y})")
        print(f"target (x, y): ({x, y})")
        # self.change_y = 20
        # move the dagger in sync with the players movement
        self.target_x, self.target_y = x, y
        self.set_direction(self.direction, 0)
        # create the throwing trajectory
        ang = physics.get_triangle(self.parent.center_x, x, self.parent.center_y, y, 100)
        self.tri = ang[1]
        self.ang = ang[0]
        path = physics.distance_trajectory(self.parent.center_x, self.parent.center_y, 30, ang[0], 3, show=False)
        self.y_values = [y[1] for y in path if y[1] >= self.parent.bottom]
        print("y_vals:", len(self.y_values))


        self.angle = self.ang - 45

        if 80 < self.ang < 90:
            self.ang_change = 180/45
        else:
            self.ang_change = 180 / 50
        # if self.ang <= 30:
        #     self.ang_change = (90 - (self.angle + 45)) / len(self.y_values)
        # elif 30 < self.ang <= 50:
        #     self.ang_change = (90 - self.angle) / len(self.y_values)
        # elif 50 < self.ang <= 60:
        #     self.ang_change = (180 - (self.angle + 45)) / len(self.y_values)
        # elif 60 < self.ang <= 66:
        #     self.ang_change = (90 - (self.angle - 45 -5)) / len(self.y_values)
        # elif 66 < self.ang <= 74:
        #     self.ang_change = (180 - (self.angle + 45 - 25)) / len(self.y_values)
        # elif 74 < self.ang <= 80:
        #     self.ang_change = (180 - (self.angle -15)) / len(self.y_values)
        # else:
        #     self.ang_change = (180 + 0) / len(self.y_values)
        print("y:", self.y_values)
        self.path = path
        self.trajectory = copy.deepcopy(path)
        self.thrown = True

    def set_direction(self, direction, speed):
        if direction == right:
            self.change_x = 0
            # self.angle = -45
            self.angle = 0
            self.center_x = self.parent.right
            self.center_y = self.parent.center_y - 14
        elif direction == left:
            self.change_x = 0
            # self.angle = 90 + 45
            self.angle = 90
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








