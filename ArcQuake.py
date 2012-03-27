# ArcQuake.py -- Python-based ArcGIS tool to interface the USGS earthquake GeoRSS 
# Author: Bryan Goodrich
#         http://www.bryangoodrich.com
# Date Created: 18 March 2012
# Last Updated: 19 March 2012
# -- Completely redesigned the RSS aggregation portion by creating the
#    getData function and using list comprehension to simplify list
#    processing. Also adapted the results into a final list of dictionary
#    entries that name each of the GeoRSS item properties that get used
#    later in creating ArcGIS geometry objects. 
# -- Added the ArcGIS section by importing appropriate modules and 
#    setting up a functioning framework that creates an empty 
#    feature class and populates it. The ESRI Desktop help pages demonstrate
#    how easy it is to access spatial references based on a user's installation
#    at http://help.arcgis.com/en/arcgisdesktop/10.0/help/index.html#//000v000000p6000000
# -- The next steps will require setting up the parameters to make this usable as
#    an ArcMap/ArcCatalog script tool and then customizing validation and additional options.

# ========== Define Imports and Library Functions ==========
import arcpy, os
from urllib           import urlopen             # used to retrieve online information
from xml.dom          import minidom             # used to parse XML content
from arcpy            import env                 # used to set workspace settings
from arcpy.management import CreateFeatureclass  # creates an empty feature class
from arcpy.management import AddField            # adds fields to the feature class


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
        d    = [reduce(lambda x, y: x + ', ' + y, text[1:])]
        d.append(text[0][2:])
        return d


    # These dictionary keys match the USGS GeoRSS item nodes
    KEYS = ['full date', 'description', 'date', 'url', 'lat', 'long', 'class',
            'set', 'depth', 'guid']
            
    # This algorithm grabs the child nodes for each node in the node list.
    # Since every node is atomic, 'child' is a singular list. The values
    # are appended to the values list to create a dictionary.
    # However, changes are required to parse the 'description' into
    # magnitude and title components that it contains. See 'fracture' above.
    nodeList = item.childNodes                   # Extract item's child nodes
    x = []                                       # List to be populated with dictionary values
    for child in [node.childNodes for node in nodeList]:
        x.append(child[0].nodeValue)             # Could use nested list comprehension, but ugh ...
    x              = dict(zip(KEYS, x))          # 'zip' pairs up keys and values
    t, m           = fracture(x['description'])  # Get title and magnitude portions
    x['depth']     = x['depth'].split(' ')[0]    # keep only number portion; remove 'km'
    x['title']     = t
    x['magnitude'] = m
    
    # Remove unnecessary/redundant dictionary entries
    del x['description'], x['set'], x['full date']
    return x
#  end function



def createFeature(outpath, projection):
    CreateFeatureclass(os.path.dirname(outpath), os.path.basename(outpath), "Point",
                       spatial_reference = projection)
    AddField(outpath,     'depth', 'FLOAT')
    AddField(outpath, 'magnitude', 'FLOAT')
    AddField(outpath,    'mclass', 'SHORT')
    AddField(outpath,  'location',  'TEXT')
    AddField(outpath,      'guid',  'TEXT')
    # AddField(outpath, 'date', 'DATE')
    # -- not sure about date formats in ArcGIS yet. Work on this later.
# end function



def checkRecord(current, data):
    query = "'\quid\' = " +  current  # Create query to match current guid to any records
    matches = arcpy.SearchCursor(data, query, fields = 'guid')  # Return guids of any matched record(s)
    if len(matches) != 0:
        return False  # Record guid is not new

    return True  # Return that no matches exist



# ========== Set Parameters and Environmental Variables ==========
# Set projection for +proj=longlat +ellps=WGS84 +datum=WGS84
prj       = "Coordinate Systems/Geographic Coordinate Systems/World/WGS 1984.prj"
prjFile   = os.path.join(arcpy.GetInstallInfo()["InstallDir"], prj)

# Get Form parameters
outpath   = arcpy.GetParameterAsText(0)
feedtype  = arcpy.GetParameterAsText(1)
overwrite = arcpy.GetParameterAsText(2)


# Capture GeoRSS XML and isolate its 'item' elements
if   feedtype == "Hour":
    url = "http://earthquake.usgs.gov/earthquakes/catalogs/eqs1hour-M0.xml"
elif feedtype == "Day":
    url = "http://earthquake.usgs.gov/earthquakes/catalogs/eqs1day-M0.xml"
else:
    url = "http://earthquake.usgs.gov/earthquakes/catalogs/eqs7day-M2.5.xml"



# ========== Begin RSS Aggregation ==========
doc   = minidom.parse(urlopen(url))        # XML document
items = doc.getElementsByTagName("item")   # Want to avoid same-name elements in root.
                                           # Returns list of 'item' document elements.
feed  = [getData(item) for item in items]  # List of item dictionary



# ========== Begin ArcGIS Representation ==========
# Create feature class and add fields for additional Quake information
if not arcpy.Exists(outpath):
    createFeature(outpath, prjFile)
elif overwrite:
    arcpy.AddMessage("Removing Old Copy of Feature Class")
    arcpy.management.Delete(outpath)
    createFeature(outpath, prjFile)


                          
# Connect to Feature Class and Populate Feature Table
cur = arcpy.InsertCursor(outpath)                  # Connects to empty Feature Class
for quake in feed:
    isNew = checkRecord(quake['quid'])             # --- NEEDS TO BE DEFINED ---
    if isNew:                                      # If quake is not in feature, add it
        feat           = cur.newRow()              # Define a new Row object on cursor
        lat            = float(quake['lat'])
        lng            = float(quake['long']) 
        pnt            = arcpy.Point(lng, lat)     # Create Point object
        feat.shape     = arcpy.PointGeometry(pnt)  # Set geometry point class
        feat.guid      = quake['quid']             # Set USGS quake guid value
        feat.depth     = float(quake['depth'])     # Set Depth
        feat.magnitude = float(quake['magnitude']) # Set Magnitude
        feat.mclass    = int(quake['class'])       # Set Magnitude Class
        feat.location  = quake['title']            # Set Location Description
        cur.insertRow(feat)                        # Populate Feature Class record
    


del cur  # Unlock table



