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



# Populate list elements with appropriate components from GeoRSS
for item in items:
    for node in item.getElementsByTagName("geo:lat"):
        lat.append(node.childNodes[0].data)

    for node in item.getElementsByTagName("geo:long"):
        lng.append(node.childNodes[0].data)

    for node in item.getElementsByTagName("dc:subject"):
        mclass.append(node.childNodes[0].data)

    for node in item.getElementsByTagName("dc:subject"):
        depth.append(node.childNodes[2].data)  # 3rd dc:subject element in items

    for node in item.getElementsByTagName("pubDate"):
        time.append(node.childNodes[0].data)

    for node in item.getElementsByTagName("title"):  # Title contains "M (mag), [title]"
        m, t = node.childNodes[0].data.split(", ")    # Break Title into components
        mag.append(m[2:])                             # Remove "M " from LHS
        title.append(t)                               # Accept RHS as-is



# Begin creating ArcGIS feature classes based on user inputs