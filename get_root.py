#!/usr/bin/env python3

import xml.etree.ElementTree as ET
tree = ET.parse('11_TGATAAs.svg')
root = tree.getroot()
print(root)
print(root.attrib)
