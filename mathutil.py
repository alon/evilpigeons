from numpy import linspace

def interpolate(n, src, dest):
    """ interpolate tuples/lists src to dest, must be same size """
    return zip(*[list(linspace(src[i], dest[i], n)) for i in xrange(len(src))])

def polygon(n, points):
    return sum([interpolate(n/len(points), points[i], points[(i+1)%len(points)]) for i in xrange(len(points))], [])

def path(n, points):
    return sum([interpolate(n/len(points), points[i], points[i+1]) for i in xrange(len(points) - 1)], [])

