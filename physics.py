import arcade
import numpy as np
import math
import items
import matplotlib.pyplot as mp
from player import Player
import time
from abc import ABC, abstractmethod
# from numba import jit
from copy import deepcopy

left = -1
right = 1


class Trajectory(ABC):

    trajectory: list

    def get_path(self):
        return self.trajectory


class PhysicsEngine:
    def __init__(self, player: Player, ground: arcade.SpriteList, targets: arcade.SpriteList, gravity, level=None):
        self.player = player
        self.surface_list = ground
        self.target_list = targets
        self.objects = arcade.SpriteList()
        self.player.physics_engine = self
        self.collider = level.collisions if level else None
        self.gravity = gravity

    def update(self):
        # self.player.update()
        # self.surface_list.update()
        # if self.objects:
            # print("objects")
        self.objects.update()

    def update_ground(self, ground_list):
        self.surface_list = ground_list

    def check_for_collision(self, sprite1, sprite2):
        pass

    def check_for_collision_with_list(self, sprite, sprite_list):
        pass

    def add_object(self, obj):
        self.objects.append(obj)

    def remove_object(self, obj):
        self.objects.remove(obj)

    def draw_trajectory(self, projectile):
        path = projectile.get_sliced(self.surface_list)
        arcade.draw_points(path, arcade.color.GOLD, 3)

    def throw_object(self, obj, x0, y0, v0):
        obj.set_trajectory(self.get_trajectory_from_player(x0, y0, v0))
        obj.on_throw()
        self.player.weapons.append(obj)
        self.add_object(obj)

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

    def throw_knife_old(self, knife: items.ThrowingKnife, x0, y0):
        # create a triangle between the player, a space in front of player, and mouse position
        tri = StaticTriangle(self.player.center_x, x0, self.player.center_y, y0, 100)
        knife.tri = tri
        dtime = Geometry.get_time(knife.speed, knife.range*64)
        # set appropriate directions
        if self.player.center_x < x0:
            direction = right
        else:
            direction = left
        # set player and knife directions
        self.player.direction = direction
        knife.set_direction(direction)
        # calculate velocity
        v = tri.hypotenuse() * knife.speed


        # prevent velocity from exceeding the specified maximum
        if v > knife.max_speed:
            v = knife.max_speed
        # get the angle to throw
        angle = tri.angle
        time_inc = .1
        # create the trajectory
        path = ProjectileTimeTrajectory(self.player.center_x, self.player.center_y, v, angle, 3, dtime, self, time_inc=time_inc)


        # slice the path at the point which it would collide with an object
        path.slice(collider=self.collider)

        # keep knife at consistent speed, regardless of precision (time increment)
        n = int(.5/time_inc)

        path.cut(n)
        # tm = time.perf_counter()

        # get the list of points from our trajectory object
        p = path.get_path()
        # dist = arcade.get_distance_between_sprites(self.player, knife)

        dx = arcade.get_distance(self.player.center_x, self.player.center_y, p[-1][0], p[-1][1])  # change in x
        print(f"dy: none dx: {dx}")

        print("vel:", v)  # total velocity
        vy = v * math.sin(math.radians(angle))  # y velocity
        vx = v * math.cos(math.radians(angle))  # x velocity
        print(f"vy: {vy}, vx: {vx}")

        time = (-vy - vy) / -3  # time
        print(f"my_time: {time}")

        # Horizontal Range
        R = abs((v**2 / -3 * (math.sin(math.radians(angle*2)))))
        r = (-vy ** 2) / -6  # vertical change

        print(f"horz range: {R} vert rnge: {r}")
        # a_change = a_change / dx
        # print(a_change)
        # a = math.degrees(math.atan2(v, 3))
        knife.set_angle(v, 3, angle)
        # print("achan:", achan)
        # knife.set_ang_change(angle, a_change)
        knife.throw(path)
        # print("time to half", time.perf_counter() - tm)

    def get_trajectory_from_player(self, x0, y0, v0, max_velocity=None):
        tri = StaticTriangle(self.player.center_x, x0, self.player.center_y, y0, 100)
        if max_velocity and v0 > max_velocity:
            v0 = max_velocity
        return ProjectileDistanceTrajectory(self.player.center_x, self.player.center_y, v0, tri.angle, 3)

    def get_knife_trajectory_from_player(self, x0, y0, knife, precision=.5):
        tri = StaticTriangle(self.player.center_x, x0, self.player.center_y, y0, 100)
        v = tri.hypotenuse() * knife.speed
        if v > knife.max_speed:
            v = knife.max_speed
        return ProjectileDistanceTrajectory(self.player.center_x, self.player.center_y, v, tri.angle, 5 , precision)

    # def get_trajectory_from_player(self, x0, y0, v0):
    #     tri = Triangle(self.player.center_x, x0, self.player.center_y, y0, 100)
    #     return ProjectileDistanceTrajectory(self.player.center_x, self.player.center_y, v0, tri.angle, self.gravity)
    def get_angle_change(self, trajectory):
        mid_point = trajectory.get_max_point()
        start_point = trajectory.x0, trajectory.y0
        end_point = trajectory.get_point_of_impact(self.surface_list)
        tri = Triangle(start_point, mid_point, end_point)
        v = trajectory.v0
        vy = v * math.sin(math.radians(tri.angle_a()))

        time = (-vy - vy) / -5  # time
        new = deepcopy(trajectory)
        new.slice_at_collision(self.surface_list)
        new.trim()
        ln = len(new.get_path())
        chng = (180 - tri.angle_b()) / (time / (1 / 3))
        # if tri.an
        if new.get_index_of_impact(self.surface_list) <= new.get_path().index(new.get_max_point()):
            chng = (90 - tri.angle_b()) / (time / (1 / 3))
        return chng

class DistanceTrajectory(Trajectory):
    def __init__(self, x0, y0, v0, angle, gravity, precision):
        self.x0, self.y0, self.v0, self.angle, self.gravity, self.precision = x0, y0, v0, angle, gravity, precision
        self.trajectory = Geometry.distance_trajectory(x0, y0, v0, angle, gravity, precision)


class TimeTrajectory(Trajectory):
    def __init__(self, x0, y0, v0, angle, gravity, dtime, time_inc):
        self.x0, self.y0, self.v0, self.angle, self.gravity = x0, y0, v0, angle, gravity
        self.trajectory = Geometry.time_trajectory(x0, y0, v0, angle, gravity, dtime, time_inc=time_inc)


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


class Geometry:

    @staticmethod
    def get_velocity(x, y):
        return math.sqrt((x ** 2) + (y ** 2))

    @staticmethod
    def get_distance(x1, y1, x2, y2):
        return math.sqrt(((x2 - x1) ** 2) + ((y2 - y1) ** 2))



    @staticmethod
    def get_triangle(point1, point2, point3):
        x1, y1 = point1
        x2, y2 = point2
        x3, y3 = point3

        # calculate the three sides using the distance formula
        c = math.sqrt(Geometry.get_distance(x1, y1, x2, y2))
        a = math.sqrt(Geometry.get_distance(x2, y2, x3, y3))
        b = math.sqrt(Geometry.get_distance(x3, y3, x1, y1))
        return a, b, c

    @staticmethod
    def get_triangle_static(x1, x2, y1, y2, r):
        # calculate the three points
        p1 = (x1, y1)
        p2 = (x1 + r, y1)
        p3 = (x2, y2)

        # calculate the three sides using the distance formula
        a = math.sqrt(((p2[0] - x1) ** 2) + ((p2[1] - y1) ** 2))
        b = math.sqrt(((p3[0] - p2[0]) ** 2) + ((p3[1] - p2[1]) ** 2))
        c = math.sqrt(((p3[0] - p1[0]) ** 2) + ((p3[1] - p1[1]) ** 2))
        # calculate the angle thrown using law of cosines
        top = (b ** 2) - (a ** 2 + c ** 2)
        bottom = -2 * a * c
        eq = top / bottom
        angle = math.acos(eq)
        sides = [math.sqrt(x) for x in (a, b, c)]
        points = p1, p2, p3
        angle = math.acos(eq)
        degrees = angle * (180 / math.pi)
        if y2 < y1:
            degrees *= -1
        # print("radians:", angle)
        # print("degrees:", angle * (180/math.pi))
        return degrees, points, sides

    @staticmethod
    def get_angle_from_velocity(vx, vy):
        angle = math.atan2(vy, vx)
        angle = math.degrees(angle)
        # angle *= -1
        return angle

    @staticmethod
    def distance_trajectory(x0, y0, v0, angle, gravity, precision=.5, floor=0):
        points = []
        # get the x and y velocities
        vx = v0 * math.cos(math.radians(angle))
        vy = v0 * math.sin(math.radians(angle))
        g = gravity
        t = 0  # time starts at 0
        y = 0
        while y >= floor:
            t += precision  # add time (higher values = less points calculated, which is faster)
            x = x0 + vx * t  # calculate x position
            y = y0 + (vy * t) - ((.5 * g) * (t ** 2))  # calculate y position
            points.append((x, y))
        return points

    @staticmethod
    # @jit
    def time_trajectory(x0, y0, v0, angle, gravity, dtime, time_inc, floor=0):
        points = []
        # get the x and y velocities
        # v0 = v0 / (time_inc / .5)
        vx = v0 * math.cos(math.radians(angle))
        vy = v0 * math.sin(math.radians(angle))
        g = gravity
        t = 0  # time starts at 0
        y = 0
        while y >= floor:
            t += time_inc  # add time (higher values = less points calculated, which is faster)
            x = x0 + vx * t  # calculate x position
            y = y0 + (vy * t) - ((.5 * g) * (t ** 2))  # calculate y position
            points.append((x, y))
        # print(t)
        return points

    @staticmethod
    def get_time(velocity, distance):
        t = distance/velocity
        return t

    def get_projectile_trajectory(self):
        pass


# def get_path(self, x1, y1, x2, y2, v, rn):
#     ang = self.get_triangle(x1, x2, y1, y2, rn)
#     path = self.distance_trajectory(x1, y1, v, ang)
#     return path


if __name__ == "__main__":
    g = Geometry()

    # calc_para((100, 10), 100, show=True, cutoff=None, scale_x=1, scale_y=1, flip_y=False, flip_x=False)
    # print(n)

    # print(f"start_x: {n[0][0]} end_x: {n[-1][0]}")


# class PhysicsEngine:
#     def __init__(self):
#         pass
#
#     def check_for_collision(self):
#         pass
#
#     def set_direction(self):
#         pass
#
# class PlayerPhysicsEngine(PhysicsEngine):
#     def __init__(self):
#         super(PlayerPhysicsEngine, self).__init__()
#
#
# class EnemyPhysicsEngine(PhysicsEngine):
#     def __init__(self):
#         super(EnemyPhysicsEngine, self).__init__()
#
#
# class ObjectPhysicsEngine(PhysicsEngine):
#     def __init__(self):
#         super(ObjectPhysicsEngine, self).__init__()


def calc_para(self, vertex: tuple, distance: float, flip_y: bool = True, flip_x: bool = False,
              cutoff: float = None, precision: float = 1, scale_x=1.0, scale_y=1.0, start: float = 0,
              show: bool = False, preserve: bool = True, output: bool = False):
    h, k = x, y, = vertex
    half = distance / 2
    if not start:
        start = h - half
    stop = start + distance
    precision = int(precision * 100)
    a = scale_x
    b = scale_y
    if flip_y:  # flip the parabola
        a *= -1
    if flip_x:
        b *= -1

    # generate x coordinates
    x = np.linspace(start, stop, precision)
    # parabola vertex formula

    # generate list of points for the parabola

    if cutoff is not None:
        y = a * (b * x - h) ** 2 + k
        # y = a * (x - h) ** 2 + (k ** 3)
        points = [(xp, yp) for xp, yp in zip(x, y) if yp >= cutoff]
    else:
        y = a * (b * x - h) ** 2 + k
        points = [(xp, yp) for xp, yp in zip(x, y)]
    if show:
        x = [x[0] for x in points]
        y = [y[1] for y in points]
        mp.plot(x, y)
        mp.show()

    if output:
        print(f"x_start: {start}, x_stop: {stop}")
        print(f"vertex: {h, k}")

    return points