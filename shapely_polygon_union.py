#!/usr/bin/env python3
import sys
import shapely

from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.ops import cascaded_union

if False:
    p1 = Polygon([(338.62, 135.47), (338.62, 135.92), (339.07, 135.92), (339.07, 135.47)])
    p2 = Polygon([(337.73, 135.47), (337.73, 135.92), (338.63, 135.92), (338.63, 135.47)])
    union = cascaded_union([p1,p2])
    print(p1)
    print(p2)
    print(union)

# how does does union handle non-overlaps
p1 = Polygon( [ (0,0), (0,1), (1,1), (1,0) ] )
p2  = Polygon( [ (1,0), (1,1), (2,1), (2,0) ] )
p3 = Polygon( [ (3,0), (3,1), (4,1), (4,0) ] )

union = cascaded_union([p1,p2,p3])
print(union)


#second round, move everything over by .1 and up by .5
p1 = Polygon( [ (0.1,0.5), (0.1,1.5), (1.1,1.5), (1.1,0.5) ] )
p2  = Polygon( [ (1.1,0.5), (1.1,1.5), (2.1,1.5), (2.1,0.5) ] )
p3 = Polygon( [ (3.1,0.5), (3.1,1.5), (4.1,1.5), (4.1,0.5) ] )

union2 = cascaded_union([union,p1,p2,p3])

import matplotlib.pyplot as plt

for p in union2:
    s = p.simplify(.05)
    plt.plot(*s.exterior.xy)

plt.show()
