import arcade
import numpy as np
import items
import matplotlib.pyplot as mp
from player import Player
from jarcade.engine import PhysicsEngine as Engine
import jarcade.shapes

left = -1
right = 1


class PhysicsEngine(Engine):
    def __init__(self, player: Player, ground: arcade.SpriteList, targets: arcade.SpriteList, gravity, level=None):
        super(PhysicsEngine, self).__init__(player, ground, targets, gravity, level)

    def throw_knife(self, x, y, knife: items.ThrowingKnife):
        trajectory = self.get_knife_trajectory_from_player(x, y, knife, .3)
        # trajectory.slice_at_collision(self.surface_list)
        # trajectory.trim()
        knife.throw(trajectory)
        # knife.triangle = tri
        # print(f"A: {a}, B: {b}, C: {c}")
        self.player.direction = left
        if x > self.player.center_x:
            self.player.direction = right
        knife.set_direction(self.player.direction)

        knife.set_angle_change(trajectory.angle, self.get_angle_change(trajectory))
        # knife.change_angle = angle_change / len(trajectory.get_sliced(self.surface_list))
        self.add_object(knife)

    def get_knife_trajectory_from_player(self, x0, y0, knife, precision=.5):
        tri = jarcade.shapes.StaticTriangle(self.player.center_x, x0, self.player.center_y, y0, 100)
        v = tri.hypotenuse() * knife.speed
        if v > knife.max_speed:
            v = knife.max_speed
        return jarcade.shapes.ProjectileDistanceTrajectory(self.player.center_x, self.player.center_y, v, tri.angle, 5, precision)