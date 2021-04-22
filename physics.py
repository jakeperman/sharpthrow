import arcade
import numpy as np
import math
import matplotlib.pyplot as mp
import time
left = 1
right = 0


class Geometry:
    def __init__(self):
        pass

    def calc_para(self, vertex: tuple, distance: float, flip_y: bool = True, flip_x: bool = False,
                  cutoff: float = None, precision: float = 1, scale_x=1.0, scale_y=1.0, start: float = 0,
                  show: bool = False, preserve: bool = True, output: bool = False):
        h, k = x, y, = vertex
        half = distance/2
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
            y = a * (b*x-h) ** 2 + k
            # y = a * (x - h) ** 2 + (k ** 3)
            points = [(xp, yp) for xp, yp in zip(x, y) if yp >= cutoff]
        else:
            y = a * (b*x-h) ** 2 + k
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

    def create_path(self, start, stop, step):
        return np.linspace(start, stop, step)

    def get_velocity(self, x, y):
        v = (x**2) + (y**2)
        v = math.sqrt(v)
        return v


def get_triangle(x1, x2, y1, y2, r):
    # calculate the three points
    p1 = (x1, y1)
    p2 = (x1 + r, y1)
    p3 = (x2, y2)

    # calculate the three sides
    a = math.sqrt(((p2[0] - x1)**2) + ((p2[1] - y1)**2))
    b = math.sqrt(((p3[0] - p2[0])**2) + ((p3[1] - p2[1])**2))
    c = math.sqrt(((p3[0] - p1[0])**2) + ((p3[1] - p1[1])**2))
    # calculate the angle thrown using law of cosines
    top = (b**2) - (a**2 + c**2)
    bottom = -2 * a * c
    eq = top/bottom
    sides = [math.sqrt(x) for x in (a, b, c)]
    points = p1, p2, p3
    angle = math.acos(eq)
    degrees = angle * (180/math.pi)
    # print("radians:", angle)
    # print("degrees:", angle * (180/math.pi))
    return degrees, points, sides


def distance_trajectory(x0, y0, v0, angle, gravity, show=False):
    x_coords = []
    y_coords = []
    # get the x and y velocities
    vx = v0 * math.cos(math.radians(angle))
    vy = v0 * math.sin(math.radians(angle))
    g = gravity
    t = 0  # time starts at 0
    y = 0
    while y >= 0:
        t += .5 # add time (higher values = less points calculated, which is faster)
        x = x0 + vx*t  # calculate x position
        y = y0 + (vy*t) - ((.5*g)*(t**2))  # calculate y position
        x_coords.append(x)
        y_coords.append(y)
    # plot the trajectory and show it
    if show:
        x = np.array(x_coords)
        y = np.array(y_coords)
        mp.plot(x, y)
        mp.show()
    points = [(x, y) for x, y in zip(x_coords, y_coords)]
    return points


def get_path(x1, y1, x2, y2, v, rn):
    ang = get_triangle(x1, x2, y1, y2, rn)
    path = distance_trajectory(x1, y1, v, ang)
    return path


if __name__ == "__main__":
    g = Geometry()

    n = g.calc_para((100, 10), 100, show=True, cutoff=None, scale_x=1, scale_y=1, flip_y=False, flip_x=False)
    print(n)

    print(f"start_x: {n[0][0]} end_x: {n[-1][0]}")


class PhysicsEngine:
    def __init__(self):
        pass

    def check_for_collision(self):
        pass

    def set_direction(self):
        pass




class PlayerPhysicsEngine(PhysicsEngine):
    def __init__(self):
        super(PlayerPhysicsEngine, self).__init__()


class EnemyPhysicsEngine(PhysicsEngine):
    def __init__(self):
        super(EnemyPhysicsEngine, self).__init__()


class ObjectPhysicsEngine(PhysicsEngine):
    def __init__(self):
        super(ObjectPhysicsEngine, self).__init__()


