import arcade
from geometry import Geometry
from abc import ABC, abstractmethod
import math


class Trajectory(ABC):

    trajectory: list

    def get_path(self):
        return self.trajectory


class DistanceTrajectory(Trajectory):
    def __init__(self, x0, y0, v0, angle, gravity, precision):
        self.x0, self.y0, self.v0, self.angle, self.gravity, self.precision = x0, y0, v0, angle, gravity, precision
        self.trajectory = Geometry.distance_trajectory(x0, y0, v0, angle, gravity, precision)


class ProjectileDistanceTrajectory(DistanceTrajectory):
    def __init__(self, x0, y0, v0, angle, gravity, precision=.5):
        super().__init__(x0, y0, v0, angle, gravity, precision)

    def draw(self):
        path = self.get_path()
        arcade.draw_points(path, arcade.color.GOLD, 3)

    def slice_at_collision(self, collision_objects: arcade.SpriteList):
        self.trajectory = self.get_sliced(collision_objects)

    def get_sliced(self, collision_objects: arcade.SpriteList):
        end_point_index = self.get_index_of_impact(collision_objects)
        new_path = self.trajectory[:end_point_index]
        trajectory = new_path
        return trajectory

    def get_trimmed_path(self):
        factor = int(.5/self.precision)
        end = self.trajectory[-2:]
        trajectory = self.trajectory[:-2:factor]
        trajectory = trajectory + end
        return trajectory

    def trim(self):
        self.trajectory = self.get_trimmed_path()
        return self.trajectory

    def get_point_of_impact(self, spritelist: arcade.SpriteList):
        end_point = None
        points_to_check = self.get_path()
        for point in points_to_check:
            if arcade.get_sprites_at_point(point, spritelist):
                end_point = point
                break
        if end_point:
            return end_point
        return points_to_check[-1]

    def get_index_of_impact(self, spritelist: arcade.SpriteList):
        point = self.get_point_of_impact(spritelist)
        return self.trajectory.index(point)

    def get_max_height(self):
        y_values = [p[1] for p in self.trajectory]
        return max(y_values)

    def get_max_point(self):
        y_values = [p[1] for p in self.trajectory]
        max_h = max(y_values)
        h_ind = y_values.index(max_h)
        point = self.trajectory[h_ind]
        return point


class Triangle:
    def __init__(self, point1: tuple, point2: tuple, point3: tuple):
        self.points = point1, point2, point3
        self.sides = Geometry.get_triangle(point1, point2, point3)

    def draw(self):
        arcade.draw_polygon_outline(self.points, arcade.color.PURPLE, 2)

    def angle_a(self):
        a, b, c = self.sides
        th = (a ** 2) - (b ** 2 + c ** 2)
        bh = -2 * b * c
        eq = th / bh
        return math.degrees(math.acos(eq))

    def angle_b(self):
        a, b, c = self.sides
        th = (b ** 2) - (a ** 2 + c ** 2)
        bh = -2 * a * c
        eq = th / bh
        return math.degrees(math.acos(eq))

    def angle_c(self):
        a, b, c = self.sides
        th = (c ** 2) - (b ** 2 + a ** 2)
        bh = -2 * a * b
        eq = th / bh
        return math.degrees(math.acos(eq))


class StaticTriangle:
    def __init__(self, x1, x2, y1, y2, r):
        self.shape = Geometry.get_triangle_static(x1, x2, y1, y2, r)
        self.points = self.shape[1]
        self.angle = self.shape[0]
        self.sides = self.shape[2]

    def draw(self):
        arcade.draw_polygon_outline(self.points, arcade.color.PURPLE, 1)

    def get_shape(self):
        return self.shape

    def hypotenuse(self):
        return self.sides[2]

    def get_angle(self):
        return self.angle