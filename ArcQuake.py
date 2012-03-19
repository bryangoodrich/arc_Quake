from urllib  import urlopen # used to retrieve online information
from xml.dom import minidom # used to parse XML content


# ========== User-defined functions ==========
def getData(item):
    # This function expects a USGS GeoRSS item.
    # Returns a Python dictionary.
    nodeList = item.childNodes  # Extract item's child nodes

    # These dictionary keys match the USGS GeoRSS item nodes
    keys = ['full date', 'description', 'date', 'url', 'lat', 'long', 'class',
            'set', 'depth', 'guid']

    # This algorithm grabs the child nodes for each node in the node list.
    # Since every node is atomic, its node list is singular. The values
    # are appended to the values list. However, changes are required to
    # parse the description that takes the form:
    #     'M [magnitude], [title]'
    #
    # The [title] component may have comma separated names. This algorithm
    # returns only the magnitude and the first portion of the title.
    # The magnitude portion includes the "M " that is parsed out. These
    # values are appended to the dictionary with appropriate keys.
    x = []  # List to be populated below to for dictionary values
    for child in [node.childNodes for node in nodeList]:
        x.append(child[0].nodeValue)
    x              = dict(zip(keys, x))
    m, t           = x['description'].split(', ')[0:2]
    x['title']     = t
    x['magnitude'] = m[2:]
    return x



# Establish user inputs here. Select appropriate url



# Capture GeoRSS XML and isolate its 'item' elements
#===== At this time, hardcoding the past hour RSS for prototyping =====
url   = "http://earthquake.usgs.gov/earthquakes/catalogs/eqs1hour-M0.xml"
doc   = minidom.parse(urlopen(url)) # XML document
items = doc.getElementsByTagName("item") # Want to avoid same-name elements in root.
                                         # Returns list of 'item' document elements.



# Populate list with dictionaries of feed item components
feed = []
for item in items:
    feed.append(getData(item))


# An example of what is contained in the Python feed object
# 'quake' is a list element that is itself a dictionary
# and 'key' is the dictionary key that is looped over in a dictionary.
for quake in feed:
    print "===== QUAKE ====="
    for key in quake:
        print key, quake[key]
    print

    
