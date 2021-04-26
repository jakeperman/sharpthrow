import arcade
import math
import numpy as np
import copy
import matplotlib.pyplot as mp
frames_per_update = 3
left = -1
right = 1



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
        self.trajectory = ()
        self.speed = 2.5
        self.ang_change = 0
        self.projectile = 0
        self.tri = None

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

    def throw(self, trajectory):
        self.projectile = trajectory
        self.path = trajectory.get_path()
        self.thrown = True

    def set_angle(self, vx, vy, angle):
        self.angle = angle - 45
        # if 80 < angle < 95:
        #     self.angle = angle - 90
        # calculate how much to change the angle each update
        a = math.degrees(math.atan2(vy, vx))
        # self.a = -(self.a)
        self.ang_change = a * .66
        if 80 < angle < 90:
            self.ang_change = a * .88

    def set_direction(self, direction):
        self.direction = direction
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