from urllib  import urlopen # used to retrieve online information
from xml.dom import minidom # used to parse XML content


# ========== User-defined functions ==========
def getData(item):
    # This function expects a USGS GeoRSS item.
    # Returns a Python dictionary.
    def fracture(text):
        # Expects the description text needing to be split. The
        # description takes on the form
        #
        #     'M [magnitude], [title]'
        #
        # The title may contain commas, so except for the first field, all
        # fields in the split are merged into a single list element.
        # The first field is then appended to the generated list, save
        # for its first 2 characters.
        #
        # This function returns a 2-element list containing title and
        # magnitude for the given quake. 
        text = text.split(', ')
        d = [reduce(lambda x, y: x + ', ' + y, text[1:])]
        d.append(text[0][2:])
        return d


    # These dictionary keys match the USGS GeoRSS item nodes
    KEYS = ['full date', 'description', 'date', 'url', 'lat', 'long', 'class',
            'set', 'depth', 'guid']
            
    nodeList = item.childNodes  # Extract item's child nodes

    # This algorithm grabs the child nodes for each node in the node list.
    # Since every node is atomic, 'child' is a singular list. The values
    # are appended to the values list to create a dictionary.
    # However, changes are required to parse the 'description' into
    # magnitude and title components that it contains. See 'fracture' above.
    x = []  # List to be populated with dictionary values
    for child in [node.childNodes for node in nodeList]:
        x.append(child[0].nodeValue)
    x              = dict(zip(KEYS, x))  # 'zip' pairs up keys and values
    t, m           = fracture(x['description'])
    x['title']     = t
    x['magnitude'] = m
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
        print key + ": ", quake[key]
    print

    
