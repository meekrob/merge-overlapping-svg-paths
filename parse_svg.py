#!/usr/bin/env python3
import sys

from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from shapely.ops import cascaded_union

filename=sys.argv[1]

import xml.etree.ElementTree as ET
tree = ET.parse(filename)
root = tree.getroot()
qname=ET.QName('{http://www.w3.org/2000/svg}')
NS='{http://www.w3.org/2000/svg}'
#NS = ''

def svg_rect_to_shapely_polygon(svg_rect):
    return Polygon( svg_rect_to_coords(svg_rect) )


def traverse( element, parent, callback, data={}):
    if 'path' not in data: data['path'] = element.tag.replace(NS,'')
    else:
        data['path'] += '/' + element.tag.replace(NS,'')

    callback(element, parent, data)
    for child in element:
        traverse( child, element, callback, data.copy() )

def reorder_by_pairs( list_of_pairs ):
    X = list_of_pairs[0]
    Y = list_of_pairs[1]
    pairs = []
    for x,y in zip(X,Y):
        pairs.append( (x,y) )

    return pairs
    

def rectify_to_shapely(rects, parent):
    polys_by_class = {}
    for rect in rects:
        if 'class' in rect.attrib:
            rect_class = rect.attrib['class']
        else: 
            rect_class = ''

        if rect_class not in polys_by_class: 
            polys_by_class[ rect_class ] = Polygon()

        new_poly = svg_rect_to_shapely_polygon( rect )

        if isinstance(polys_by_class[ css_class ], type(MultiPolygon())):
            polylist = [ p for p in polys_by_class[ css_class ] ] # turn into a list of polygons
        else:
            polylist = [polys_by_class[ css_class ]]

        overlapped = False
        for poly_i in range( len(polylist) ):
            if poly.overlaps( new_poly ):
                polylist[ poly_i ] = cascaded_union( [ polylist[ poly_i ], new_poly ] )  # should never produce a MultiPolygon
                overlapped = True
                break

        if not overlapped:
            polylist.append( new_poly )
                
        polys_by_class[ rect_class ] = polylist

        # all rects are converted to polygons, so delete each one
        parent.remove(rect)

    for css_class in polys_by_class:

        if isinstance(polys_by_class[ css_class ], type(MultiPolygon())):
            polylist = polys_by_class[ css_class ]
        else:
            polylist = [ polys_by_class[ css_class ] ]
            
        for polygon in polylist:
            simplified = polygon.simplify(.05)
            pathstring = list_to_svg_path_d( reorder_by_pairs(simplified.exterior.xy) )
            ET.SubElement( parent, NS + 'path', {'class': css_class, 'd': pathstring } )
            

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

    for rect_class, rect_elements in class_count.items():

        # create new element to substitute all the rects
        rect = rect_elements[-1]

        # adding deletion function inside merge
        polygon = merge_rect_list( rect_elements, parent )
        pathstring = list_to_svg_path_d( reorder_by_pairs(polygon) )
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

    return d + 'z'

def svg_rect_to_coords( rect ):
    precision = 8
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

    return coords

def merge_rect_into_polygon(svg_rect, svg_parent, polygon):
    # for intersecting points between the rect and polygon, 
    # replace with the rect's non-intersecting points

    rect = svg_rect_to_coords(svg_rect)
    match_point = None
    points_to_insert = []
    i = -1
    for which_corner, corner in zip(['ll','ul','ur','lr'], rect):
        try:
            i = polygon.index( corner )
        except:
            points_to_insert.append( corner )
            continue

        if match_point == None: 
            match_point = i

        # delete point from polygon
        polygon.pop(i)


    if i >= 0:
        # delete the rect 
        try:
            svg_parent.remove(svg_rect)
        except:
            sys.exit(1)

        for new_point in points_to_insert:
            polygon.insert( i, new_point )
            i += 1
            
    return polygon

def examine_rect(element, parent, data):
    if element.tag == NS + 'rect':
        return
    else:
        rects = list(element.findall(NS + 'rect'))
        nrects = len(rects)
        if nrects > 1:
            data['nrects'] = nrects
            #rectify(rects,element)
            rectify_to_shapely(rects,element)
    
#for i,child in enumerate(root):
#   print('type(root)', type(root), file=sys.stderr)
#   traverse( child, root, examine_rect)

for i,group in enumerate(root.iter(NS + 'g')):
    traverse( group, root, examine_rect, {'path': 'svg'})

# unbelievable
import xml.dom.minidom as md
mdxml = md.parseString(ET.tostring(root))
outf = open('process.svg', 'w')
outf.write(mdxml.toprettyxml())
