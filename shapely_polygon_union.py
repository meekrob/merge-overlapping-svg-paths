#!/usr/bin/env python3
import sys
import shapely

from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.ops import cascaded_union

p1 = Polygon([(338.62, 135.47), (338.62, 135.92), (339.07, 135.92), (339.07, 135.47)])
p2 = Polygon([(337.73, 135.47), (337.73, 135.92), (338.63, 135.92), (338.63, 135.47)])
union = cascaded_union([p1,p2])
print(p1)
print(p2)
print(union)

