import math
import matplotlib.pyplot as mp
import numpy as np
import time

def distance_trajectory(x0, y0, v0, angle, gravity, show=False, floor=0):
    x_coords = []
    y_coords = []
    # get the x and y velocities
    vx = v0 * math.cos(math.radians(angle))
    vy = v0 * math.sin(math.radians(angle))
    g = gravity
    t = 0  # time starts at 0
    y = 0
#    s = time.perf_counter()
    while y >= floor:
        t += .5  # add time (higher values = less points calculated, which is faster)
        x = x0 + vx * t  # calculate x position
        y = y0 + (vy * t) - ((.5 * g) * (t ** 2))  # calculate y position
        x_coords.append(x)
        y_coords.append(y)
#    print(f"time:{time.perf_counter() - s}")
    # plot the trajectory and show it
    if show:
        x = np.array(x_coords)
        y = np.array(y_coords)
        mp.plot(x, y)
        mp.show()
    points = [(x, y) for x, y in zip(x_coords, y_coords)]
    return points
    

s = time.perf_counter()
for x in range(2):
    distance_trajectory(10, -20, 30, 30, 4, True, -100)
    
print(f"total time: {time.perf_counter() - s}")