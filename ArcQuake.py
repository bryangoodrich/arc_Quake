import arcpy, os
from urllib  import urlopen # used to retrieve online information
from xml.dom import minidom # used to parse XML content
from arcpy   import env     # used to set workspace environments
from arcpy.management import CreateFeatureclass
from arcpy.management import AddField


# ========== User-defined functions ==========
def getData(item):
    # This function expects a USGS GeoRSS item.
    # Returns a Python dictionary.
    def fracture(text):
        # Expects the description text needing to be split. The
        # description takes on the form
        #
        # 'M [magnitude], [title]'
        # 'M 2.3, Northern California, California' (example)
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
            
    nodeList = item.childNodes # Extract item's child nodes

    # This algorithm grabs the child nodes for each node in the node list.
    # Since every node is atomic, 'child' is a singular list. The values
    # are appended to the values list to create a dictionary.
    # However, changes are required to parse the 'description' into
    # magnitude and title components that it contains. See 'fracture' above.
    x = [] # List to be populated with dictionary values
    for child in [node.childNodes for node in nodeList]:
        x.append(child[0].nodeValue)
    x = dict(zip(KEYS, x)) # 'zip' pairs up keys and values
    t, m = fracture(x['description'])
    x['depth'] = x['depth'].split(' ')[0]  # keep only number portion; remove 'km'
    x['title'] = t
    x['magnitude'] = m
    return x



# Establish user inputs here. Select appropriate url
# outpath = arcpy.GetParameterAsText(0) ...
env.overwriteOutput = True


# Capture GeoRSS XML and isolate its 'item' elements
#===== At this time, hardcoding the past hour RSS for prototyping =====
#url   = "http://earthquake.usgs.gov/earthquakes/catalogs/eqs1hour-M0.xml"   # Past Hour
#url   = "http://earthquake.usgs.gov/earthquakes/catalogs/eqs1day-M0.xml"    # Past Day
url   = "http://earthquake.usgs.gov/earthquakes/catalogs/eqs7day-M2.5.xml"  # Past Week
doc   = minidom.parse(urlopen(url)) # XML document
items = doc.getElementsByTagName("item") # Want to avoid same-name elements in root.
                                         # Returns list of 'item' document elements.



# Populate list with dictionaries of feed item components.
# All dictionary entries will be text.
feed = []
for item in items:
    feed.append(getData(item))



# Set projection for +proj=longlat +ellps=WGS84 +datum=WGS84
prj     = "Coordinate Systems/Geographic Coordinate Systems/World/WGS 1984.prj"
prjFile = os.path.join(arcpy.GetInstallInfo()["InstallDir"], prj)
opath   = "C:/temp/py/quake.shp"  # Hardcode location for prototyping



# Create feature class and add fields for additional Quake information
CreateFeatureclass(os.path.dirname(opath), os.path.basename(opath), "Point",
                   spatial_reference = prjFile)
AddField(opath,     'depth', 'FLOAT')
AddField(opath, 'magnitude', 'FLOAT')
AddField(opath,    'mclass', 'SHORT')
AddField(opath,  'location', ' TEXT')
# AddField(opath, 'date', 'DATE')
# -- not sure about date formats in ArcGIS yet. Work on this later.
                          


# 
cur = arcpy.InsertCursor(opath)                # Connect to empty Feature Class.
for quake in feed:                             # Convert Python data to appropriate
    lat            = float(quake['lat'])       # data types when stored in feature
    lng            = float(quake['long'])      # class. 
    pnt            = arcpy.Point(lng, lat) 
    feat           = cur.newRow()
    feat.shape     = arcpy.PointGeometry(pnt)  # Set geometry point class
    feat.depth     = float(quake['depth'])
    feat.magnitude = float(quake['magnitude'])
    feat.mclass    = int(quake['class'])
    feat.location  = quake['title']
    cur.insertRow(feat)
    

del cur  # Unlock table
