from numpy import linspace

def interpolate(n, (x0, y0), (x1, y1)):
    return zip(list(linspace(x0, x1, n)), list(linspace(y0, y1, n)))

def polygon(n, points):
    return sum([interpolate(n/len(points), points[i], points[(i+1)%len(points)]) for i in xrange(len(points))], [])

def path(n, points):
    return sum([interpolate(n/len(points), points[i], points[i+1]) for i in xrange(len(points) - 1)], [])

