#!/usr/bin/env python3

def list_to_svg_path_d(l):
    command = 'm'
    d = ''
    for point in l:
        d += "%s %.2f,%.2f " % (command,point[0],point[1])
        command = 'l'

    return d + 'z'
    

def merge_rect_into_polygon(rect, polygon):
    # for intersecting points between the rect and polygon, replace with the rect's non-intersecting points
    match_point = None
    points_to_insert = []
    for corner in rect:
        try:
            i = polygon.index( corner )
            print('found:', corner, "==", polygon[i])
        except:
            points_to_insert.append( corner )
            continue

        if match_point == None: 
            match_point = i

        print('match_point:', match_point)

        polygon.pop(i)

    for new_point in points_to_insert:
        polygon.insert( i, new_point )
        i += 1
            
    return polygon

rect1 = [ (0,0), (0,1), (1,1), (1,0) ]
rect2 = [ (1,0), (1,1), (2,1), (2,0) ]
rect3 = [ (0,1), (0,2), (1,2), (1,1) ]
rect4 = [ (1,1), (1,2), (2,2), (2,1) ]

p = rect1
print("polygon", p)
print("###############\n")

print("rect2", rect2)
p = merge_rect_into_polygon(rect2, p)
print("polygon", p)
print("###############\n")

print("rect3", rect3)
p = merge_rect_into_polygon(rect3, p)
print("polygon", p)
print("###############\n")

print("rect4", rect4)
p = merge_rect_into_polygon(rect4, p)
print("polygon", p)

print( list_to_svg_path_d(p) )
