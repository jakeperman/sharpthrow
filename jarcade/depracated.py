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