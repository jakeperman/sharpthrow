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

    def calc_para(self, vertex: tuple, distance: float, flipped: bool = True,
                  cutoff: float = None, precision: int = 1, show: bool = False, preserve: bool = True):
        h, k = x, y, = vertex
        half = distance/2
        start, stop, = h - half, h + half
        precision = precision * 100
        a = 1
        if flipped:  # flip the parabola
            a *= -1
        # generate x coordinates
        x = np.linspace(-1, 1, precision)
        # parabola vertex formula

        # generate list of points for the parabola

        if cutoff is not None:
            y = a * (x - h) ** 2 + k
            # y = a * (x - h) ** 2 + (k ** 3)
            points = [(xp, yp) for xp, yp in zip(x, y) if yp >= cutoff]
        else:
            y = a * (x - h) ** 2 + k
            points = [(xp, yp) for xp, yp in zip(x, y)]
        if show:
            x = [x[0] for x in points]
            y = [y[1] for y in points]
            mp.plot(x, y)
            mp.show()
        return points

    def create_path(self, start, stop, step):
        return np.linspace(start, stop, step)

    def get_velocity(self, x, y):
        v = (x**2) + (y**2)
        v = math.sqrt(v)
        return v


if __name__ == "__main__":
    g = Geometry()

    n = g.calc_para((100, 10), 50, show=True, cutoff=0)
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


