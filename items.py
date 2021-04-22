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
        self.target_x, self.target_y = x, y
        # calculate direction to throw
        if self.parent.center_x < x:
            self.direction = right
        elif self.parent.center_x > x:
            self.direction = left
        # set directions for player and self
        self.parent.set_direction(self.direction)
        self.set_direction(self.direction)
        # calculate the angle the projectile was thrown
        ang = physics.get_triangle(self.parent.center_x, x, self.parent.center_y, y, 100)
        # get calculated triangle and angle thrown
        self.tri = ang[1]
        self.ang = ang[0]
        # set the velocity equal to the hypotenuse * 2.5
        v = ang[2][2] * 2.5
        # maximum velocity
        if v > 35:
            v = 35
        # get the path for the knife to follow
        path = physics.distance_trajectory(self.parent.center_x, self.parent.center_y, v, ang[0], 3, show=False)
        # generate y-values above player
        self.y_values = [y[1] for y in path if y[1] >= self.parent.bottom]
        # set initial angle of the knife
        self.angle = self.ang - 45
        # calculate how much to change the angle each update
        if 80 < self.ang < 90:
            self.ang_change = 180/45
        else:
            self.ang_change = 180 / 50
        # external access variables
        self.path = path
        self.trajectory = copy.deepcopy(path)
        self.thrown = True

    def set_direction(self, direction):
        if direction == right:
            self.change_x = 0
            self.angle = 0
            self.center_x = self.parent.right
            self.center_y = self.parent.center_y - 14
        elif direction == left:
            self.change_x = 0
            self.angle = 90
            self.center_x = self.parent.left
            self.center_y = self.parent.center_y - 10









