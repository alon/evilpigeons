# Copyright Evil Pegions team Global Game Jam 2010:
#  Simon Reisman
#  Omer Nainudel
#  Ori Cohen
#  Alon Levy
#
# This code is licensed under the Creative Commons License. For further details,
# see the LICENSE

# used to be from numpy, but to avoid this requirement we implement it ourselves
def linspace(start, end, n):
    d = float(end - start) / n
    return [start + d * i for i in xrange(n+1)]

def interpolate(n, src, dest):
    """ interpolate tuples/lists src to dest, must be same size """
    return zip(*[list(linspace(src[i], dest[i], n)) for i in xrange(len(src))])

def polygon(n, points):
    return sum([interpolate(n/len(points), points[i], points[(i+1)%len(points)]) for i in xrange(len(points))], [])

def path(n, points):
    return sum([interpolate(n/len(points), points[i], points[i+1]) for i in xrange(len(points) - 1)], [])

