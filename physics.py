import arcade
import numpy as np
import math
import items
import matplotlib.pyplot as mp
from player import Player
import time

left = -1
right = 1


class PhysicsEngine:
    def __init__(self, player: Player, ground: arcade.SpriteList, enemies: arcade.SpriteList = None):
        self.player = player
        self.ground_list = ground
        self.objects = arcade.SpriteList()
        self.player.physics_engine = self

    def update(self):
        self.player.update()
        self.ground_list.update()
        if self.objects:
            self.objects.update()

    def check_for_collision(self, sprite1, sprite2):
        pass

    def check_for_collision_with_list(self, sprite, sprite_list):
        pass

    def get_end_point(self, trajectory, return_index: bool = False):
        index = [p for p in trajectory if arcade.get_sprites_at_point(p, self.ground_list)]
        if index:
            index = trajectory.index(index[0])
        else:
            if return_index:
                return len(trajectory) - 1
            else:
                return trajectory[-1]
        if return_index:
            return index
        return trajectory[index]

    def draw_trajectory(self, trajectory):
        end = self.get_end_point(trajectory, return_index=True)
        path = trajectory[:end]
        arcade.draw_points(path, arcade.color.GOLD, 3)

    def draw_triangle(self):
        pass

    def add_object(self, obj):
        self.objects.append(obj)

    def throw_knife(self, knife: items.ThrowingKnife, x0, y0):
        # create a triangle between the player, a space in front of player, and mouse position
        tri = Triangle(self.player.center_x, x0, self.player.center_y, y0, 100)
        knife.tri = tri
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
        angle = tri.angle
        path = ProjectileTrajectory(self.player.center_x, self.player.center_y, v, angle, 3, self)
        knife.set_angle(v, 3, angle)
        knife.throw(path)

    def get_trajectory(self, x0, y0, sp=2.5):
        tri = Triangle(self.player.center_x, x0, self.player.center_y, y0, 100)
        v = tri.hypotenuse() * sp
        ang = tri.angle
        path = ProjectileTrajectory(self.player.center_x, self.player.center_y, v, ang, 3, self)
        return path


class Trajectory:
    def __init__(self, x0, y0, v0, angle, gravity):
        self.x0, self.y0, self.v0, self.angle, self.gravity = x0, y0, v0, angle, gravity
        self.trajectory = Geometry.distance_trajectory(x0, y0, v0, angle, gravity)

    def get_path(self):
        return self.trajectory


class ProjectileTrajectory(Trajectory):
    def __init__(self, x0, y0, v0, angle, gravity, physics_engine: PhysicsEngine):
        super().__init__(x0, y0, v0, angle, gravity)
        self.trajectory = Geometry.distance_trajectory(x0, y0, v0, angle, gravity)
        self.physics_engine = physics_engine

    def draw(self):
        end_point = self.physics_engine.get_end_point(self.trajectory, return_index=True)
        new_path = self.trajectory[:end_point]
        arcade.draw_points(new_path, arcade.color.GOLD, 3)

    def slice(self):
        end_point = self.physics_engine.get_end_point(self.trajectory, return_index=True)
        new_path = self.trajectory[:end_point]
        self.trajectory = new_path
        return self.trajectory


class Triangle:
    def __init__(self, x1, x2, y1, y2, r):
        self.shape = Geometry.get_triangle(x1, x2, y1, y2, r)
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
    def get_angle_b(a, b, c):
        # law of cosine for angle B
        top = (b ** 2) - (a ** 2 + c ** 2)
        bottom = -2 * a * c
        eq = top / bottom  # top of equation / bottom
        return math.degrees(math.acos(eq))  # return inverse cosine

    @staticmethod
    def get_triangle(x1, x2, y1, y2, r):
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
    def distance_trajectory(x0, y0, v0, angle, gravity, show=False, floor=0):
        x_coords = []
        y_coords = []
        # get the x and y velocities
        vx = v0 * math.cos(math.radians(angle))
        vy = v0 * math.sin(math.radians(angle))
        g = gravity
        t = 0  # time starts at 0
        y = 0
        s = time.perf_counter()
        while y >= floor:
            t += .5  # add time (higher values = less points calculated, which is faster)
            x = x0 + vx * t  # calculate x position
            y = y0 + (vy * t) - ((.5 * g) * (t ** 2))  # calculate y position
            x_coords.append(x)
            y_coords.append(y)
        # plot the trajectory and show it
        # if show:
        #     x = np.array(x_coords)
        #     y = np.array(y_coords)
        #     mp.plot(x, y)
        #     mp.show()
        points = [(x, y) for x, y in zip(x_coords, y_coords)]
        return points


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