#!/usr/bin/env python3

import xml.etree.ElementTree as ET
tree = ET.parse('11_TGATAAs.svg')
root = tree.getroot()

children = list( root )
print(len(children), "direct children")

for child in children:
    print(child.tag, child.attrib)
