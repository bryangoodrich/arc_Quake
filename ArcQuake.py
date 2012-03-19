# import arcpy
from urllib  import urlopen  # used to retrieve online information
from xml.dom import minidom  # used to parse XML content



# Establish user inputs here. Select appropriate url



# Capture GeoRSS XML and isolate its 'item' elements
#===== At this time, hardcoding the past hour RSS for prototyping =====
url   = "http://earthquake.usgs.gov/earthquakes/catalogs/eqs1hour-M0.xml"
doc   = minidom.parse(urlopen(url))       # XML document
items = doc.getElementsByTagName("item")  # Want to avoid same-name elemtns in root



# Initialize Python list elements for attributes
lat    = []  # Latitude
lng    = []  # Longitude
depth  = []  # Depth of quake (km)
title  = []  # Description of location
mag    = []  # Magnitude of quake
mclass = []  # Class of magnitude (integer)
time   = []  # Timestamp of event



# Populate list elements with appropriate components from GeoRSS.
# Each node below contains only 1 child node--viz., its own content.
for item in items:
    nodes = item.getElementsByTagName("geo:lat")
    lat.append(nodes[0].childNodes[0].data)     # Only 1 lat node

    nodes = item.getElementsByTagName("geo:long")
    lng.append(nodes[0].childNodes[0].data)     # Only 1 lng node

    nodes = item.getElementsByTagName("dc:subject")
    mclass.append(nodes[0].childNodes[0].data)  # mclass is 1st subject

    nodes = item.getElementsByTagName("dc:subject")
    depth.append(nodes[2].childNodes[0].data)   # depth is 3rd subject

    nodes = item.getElementsByTagName("pubDate")
    time.append(nodes[0].childNodes[0].data)    # Only 1 date node

    nodes = item.getElementsByTagName("title")  # Title contains "M (mag), [title]"
    m, t = node.childNodes[0].data.split(", ")  # Break Title into components
    mag.append(m[2:])                           # Ignore 1st 2 characters from LHS
    title.append(t)                             # Accept RHS as-is



# Begin creating ArcGIS feature classes based on user inputs