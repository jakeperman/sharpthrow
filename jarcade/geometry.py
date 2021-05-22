import math


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
    def get_time(velocity, distance):
        t = distance/velocity
        return t

    def get_projectile_trajectory(self):
        pass