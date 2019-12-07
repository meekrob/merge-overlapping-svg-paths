#!/usr/bin/env python3
import sys

filename=sys.argv[1]

import xml.etree.ElementTree as ET
#tree = ET.parse('11_TGATAAs.svg')
tree = ET.parse(filename)
root = tree.getroot()
qname=ET.QName('{http://www.w3.org/2000/svg}')
NS='{http://www.w3.org/2000/svg}'
#NS = ''

def traverse( element, parent, callback, data={}):
    if 'path' not in data: data['path'] = element.tag.replace(NS,'')
    else:
        data['path'] += '/' + element.tag.replace(NS,'')

    callback(element, parent, data)
    for child in element:
        traverse( child, element, callback, data.copy() )

def rectify(rects, parent):
    class_count = {}
    for rect in rects:
        if 'class' in rect.attrib:
            rect_class = rect.attrib['class']
        else: 
            rect_class = ''

        if rect_class not in class_count: 
            class_count[ rect_class ] = []

        class_count[ rect_class ].append( rect )

    print("about to merge %d rects from parent:" % len(rects), parent, parent.attrib, file=sys.stderr)

    for rect_class, rect_elements in class_count.items():

        # create new element to substitute all the rects
        rect = rect_elements[-1]

        # adding deletion function inside merge
        polygon = merge_rect_list( rect_elements, parent )
        pathstring = list_to_svg_path_d( polygon )
        try:
            ET.SubElement( parent, NS + 'path', {'class': rect_class, 'd': pathstring } )
        except:
            print("error:", sys.exc_info()[0], file=sys.stderr)
            sys.exit(1)

        
def merge_rect_list(rect_elements, parent):
    rect = rect_elements[0]

    polygon = svg_rect_to_coords(rect_elements[0])
    for next_rect in rect_elements[1:]:
        polygon = merge_rect_into_polygon( next_rect, parent, polygon)

    return polygon

def list_to_svg_path_d(l):
    command = 'M'
    d = ''
    for point in l:
        try:
            d += "%s %s,%s " % (command,point[0],point[1])
            command = 'L'
        except:
            print("quitting with", sys.exc_info()[0], file=sys.stderr)
            print(command, point, file=sys.stderr)
            raise

    print(d, file=sys.stderr)
    return d + 'z'

def svg_rect_to_coords( rect ):
    precision = 4
    try:
        x = round(float( rect.attrib['x'] ), precision)
        y = round( float( rect.attrib['y'] ), precision)
        width = round( float( rect.attrib['width'] ), precision)
        height = round( float( rect.attrib['height'] ), precision)
    except:
        print("quitting with", sys.exc_info()[0], file=sys.stderr)
        print('type(rect)',type(rect),file=sys.stderr)
        print("rect", rect, file=sys.stderr)
        print("rect.attrib", rect.attrib, file=sys.stderr)
        raise 

    # clockwise starting with lower left (x,y)
    coords = [ ( x, y ),
               ( x, round(y+height, precision) ),
               ( round(x+width, precision), round(y+height, precision) ),
               ( round(x+width, precision), y) ]

    print(coords, file=sys.stderr)
    return coords

def merge_rect_into_polygon(svg_rect, svg_parent, polygon):
    # for intersecting points between the rect and polygon, 
    # replace with the rect's non-intersecting points

    rect = svg_rect_to_coords(svg_rect)
    match_point = None
    points_to_insert = []
    i = -1
    for corner in rect:
        try:
            i = polygon.index( corner )
            print('found:', corner, "==", polygon[i])
        except:
            points_to_insert.append( corner )
            continue

        if match_point == None: 
            match_point = i

        #print('match_point:', match_point)

        polygon.pop(i)

    #if i == -1: # no overlap
        #print("polygon does not overlap rect", file=sys.stderr)
        #print("polygon:", polygon, file=sys.stderr)
        #print("rect:", rect, file=sys.stderr)
        #sys.exit(1)
        #return polygon

    if i >= 0:
        # delete the rect 
        try:
            svg_parent.remove(svg_rect)
            #for rect in rect_elements: 
                #parent.remove(rect)
        except:
            #print('type(parent)', type(parent), file=sys.stderr)
            #print('parent', parent, parent.tag, parent.attrib, file=sys.stderr)
            print('rect', rect, rect.attrib, file=sys.stderr)
            print("error:", sys.exc_info()[0], file=sys.stderr)
            sys.exit(1)

        for new_point in points_to_insert:
            polygon.insert( i, new_point )
            i += 1
            
    print(polygon, file=sys.stderr)
    return polygon

def examine_rect(element, parent, data):
    if element.tag == NS + 'rect':
        return
    else:
        rects = list(element.findall(NS + 'rect'))
        nrects = len(rects)
        if nrects > 1:
            data['nrects'] = nrects
            print(data)

            if parent: print(parent.tag, parent.attrib)

            print('class(rects[0])', type(rects[0]), file=sys.stderr)
            rectify(rects,element)
    
#for i,child in enumerate(root):
#   print('type(root)', type(root), file=sys.stderr)
#   traverse( child, root, examine_rect)

for i,group in enumerate(root.iter(NS + 'g')):
    print('type(root)', type(root), file=sys.stderr)
    traverse( group, root, examine_rect, {'path': 'svg'})



tree.write('processed.svg')
