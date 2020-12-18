import ee
import geemap
from datetime import datetime
import numpy as np
ee.Initialize()

###############
# Import Polygon
import json
f = "../MARCHIQUITA.json"
with open(f) as json_file:
    data = json.load(json_file)

# This one is geodesic 
marChiquita = ee.Geometry.Polygon(data["coordinates"])
# This one is planar
#var planarPolygon = ee.Geometry(polygon, null, false);


"""
print(coll.size().getInfo())
L = ee.Image(coll.toList(coll.size()).get(1))
print(L.getInfo()["id"])
"""

"""
var get_surface = function(img) {
  var areaImage = img.multiply(ee.Image.pixelArea());
  var stats = areaImage.reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: region,
    scale: 30,
    maxPixels: 1e9})
  return stats
  };
  // Function to calculate the mNDWI
var addmNDWI = function(image) {
  var mNDWI = image.normalizedDifference(['B3', 'B6']).rename('mNDWI');
  return image.addBands(mNDWI);
};
 
print(Land8Collection)
var withmNDWI = Land8Collection.map(addmNDWI);

// Function to define flooded / partially flooded area
var flood = function(image) {
  var mndwi = image.select(['mNDWI']);
  var noflood =  mndwi.lt(-0.35).rename('noflood');
  var partflood =  mndwi.lt(0.5).and(mndwi.gt(-0.35)).rename('pflooded');
  var fullflood = mndwi.gt(0.5).rename('flooded')
  var im = image.addBands(partflood)
  var im = im.addBands(fullflood)
  var im = im.addBands(noflood)
  return im
};
"""
# Pour get surface : img.select()

def addMaskCloud(image):
   cloud = ee.Algorithms.Landsat.simpleCloudScore(image).select('cloud')
   clouds = cloud.rename('CLOUDS');
   clouds = clouds.gt(90).rename('CLOUDS');
   im = image.addBands(clouds)
   return im

def get_surface(img):
   areaImage = img.multiply(ee.Image.pixelArea())
   stats = areaImage.reduceRegion(reducer =  ee.Reducer.sum(),\
      geometry = marChiquita,\
      scale= 30,\
      maxPixels= 1e9)
   return stats
   
def get_cloud_feature(img):
    date = img.get('system:time_start');
    stats = get_surface(img.select("CLOUDS")).get("CLOUDS")
    ft = ee.Feature(None, {'date': ee.Date(date).format('Y/M/d'), 
            'cloudRegion': ee.Number(stats).divide(marChiquita.area()).multiply(100),
    });
    #.divide(marChiquita.area)
    return ft

def convert_date(d):
    d0 = datetime.strptime(d, '%Y/%m/%d').date()
    return d0   

# content is the content of the image collection -> to load directly 
#i = 10
#img = ee.Image(content[i])
"""
date = img.get('system:time_start')
date = ee.Date(date).format('Y/M/d')
"""

##############################

threshold = 0.05

##############################

# TOA for CLOUDS
collection = ee.ImageCollection("LANDSAT/LC08/C01/T1_TOA")
coll = collection.filter(ee.Filter.eq('WRS_PATH', 229)).filter(ee.Filter.eq('WRS_ROW', 81));

cl = coll.map(addMaskCloud)
cl = cl.select("CLOUDS")
clstat = cl.map(get_cloud_feature)
stat = clstat.getInfo()
#
dates = [convert_date(s["properties"]['date']) for s in stat["features"]]
score = [s["properties"]['cloudRegion'] for s in stat["features"]]
#

print("***************")
print("DATE 1- 229081")
for d, s in zip(dates, score):
   print(d,s)
print("***************")


retain229081 = [dates[i] for i in range(len(dates)) if score[i]<threshold] 
retainscore229081 = [score[i] for i in range(len(dates)) if score[i]<threshold] 

##############################
collection = ee.ImageCollection("LANDSAT/LC08/C01/T1_TOA")
coll = collection.filter(ee.Filter.eq('WRS_PATH', 228)).filter(ee.Filter.eq('WRS_ROW', 81));

######
A = coll.getInfo()
content = [A["features"][i]["id"] for i in range(len(A["features"]))]
######

cl = coll.map(addMaskCloud)
cl = cl.select("CLOUDS")
clstat = cl.map(get_cloud_feature)
stat = clstat.getInfo()
#
dates = [convert_date(s["properties"]['date']) for s in stat["features"]]
score = [s["properties"]['cloudRegion'] for s in stat["features"]]
#

print("***************")
print("DATE 2 - 228081")
for d, s in zip(dates, score):
   print(d,s)
print("***************")

retain228081 = [dates[i] for i in range(len(dates)) if score[i]<threshold] 
retainscore228081 = [score[i] for i in range(len(dates)) if score[i]<threshold] 

##############################

Ldates = []
Lscore = []
date1 = retain228081
score1 = retainscore228081
date2 = retain229081
score2 = retainscore229081



for l, d2 in enumerate(date2): 
    delta = [np.abs((d2-dd).days) for dd in date1]
    i = np.argmin(delta)
    #
    if delta[i] <15:
        
        Ldates.append([d2.strftime("%Y%m%d"), date1[i].strftime("%Y%m%d")])
        #Ldates.append([d1.strftime("%d/%m/%y"), date2[i].strftime("%d/%m/%y")])
        Lscore.append([score2[l], score1[i]])


for l,s in zip(Ldates, Lscore):
   print("*")
   print("{0}: {1}".format(l[0], s[0]))
   print("{0}: {1}".format(l[1], s[1]))

def get_image(dd):
   d2 = dd[0]; d1 = dd[1]
   im1 = "LANDSAT/LC08/C01/T1_SR/LC08_228081_{0}".format(d1)
   im2 = "LANDSAT/LC08/C01/T1_SR/LC08_229081_{0}".format(d2)
   IMAGE = ee.ImageCollection.fromImages([ee.Image(im1), ee.Image(im2)]).median()
   return IMAGE

   

#####################
#
# MAP with everything

"""
m = geemap.Map(location=[-30, -64], zoom_start=8)
#m.centerObject(pt, 13);

for i,dd in enumerate(Ldates):
    print("{0}/{1}".format(i, len(Ldates)) )
    IMAGE = get_image(dd)
    name = "{0}: {1}-{2} ({3},{4})".format(i,dd[0],dd[1],Lscore[i][0],Lscore[i][1])
    m.addLayer(IMAGE, vis_params = {"bands": ['B4', 'B3', 'B2'], "min": 0, "max": 2000}, name = name, shown = False)
m.addLayer(marChiquita, {}, 'Polygon', opacity = 0.5)

#m.addLayer(im1, {"bands": ['CLOUDS'], "min": 0, "max": 1}, 'clouds')
m.save('dates.html')
"""
# To remove : 
#[4,9,10,11,17,18,29,36,37, 38, 41, 45]

#####################
#
exclusion = [15,14,10]
# Then map with "suspect" elements
for k, dd in enumerate(Ldates):
    d229 = dd[0]; d228 = dd[1]
    if k not in exclusion:
        print("Dpair['{0}'] = get_pair('{0}', '{1}')".format(d229, d228))   


#####################
#
# A partir de la vérification visuel refaire le tri



"""
# Get Landsat collection
collection = ee.ImageCollection("LANDSAT/LC08/C01/T1_TOA")
#collection = collection.filterDate('2017-04-11', '2020-01-01')
coll = collection.filter(ee.Filter.eq('WRS_PATH', 229)).filter(ee.Filter.eq('WRS_ROW', 81));
#
A = coll.getInfo()
content = [A["features"][i]["id"] for i in range(len(A["features"]))]
#
cl = coll.map(addMaskCloud)
print(cl.getInfo())
"""
#cl = cl.select("CLOUDS")
#clstat = cl.map(get_cloud_feature)

#print(clstat.getInfo())

# OK stats clouds < 1000

# Test Folium
# Plus meilleur image folium -> dimension
"""
m = geemap.Map(location=[-30, -64], zoom_start=8)
#m.centerObject(pt, 13);
m.addLayer(marChiquita, {}, 'Polygon')
m.addLayer(img, {"bands": ['B4', 'B3', 'B2'], "min": 0, "max": 2000}, 'colors')
m.addLayer(im1, {"bands": ['CLOUDS'], "min": 0, "max": 1}, 'clouds')
m.save('index.html')
"""
#https://github.com/giswqs/qgis-earthengine-examples/blob/master/Folium/ee-api-folium-setup.ipynb
# See equivalent basemap ? 
"""
m = folium.Map(location=[45.5236, -122.6750])
Map.addLayerControl() # This line is not needed for ipyleaflet-based Map.
m.save('index.html')
#my_map.add_ee_layer(holePoly, {}, 'Polygon')
#my_map.add_ee_layer(fc, {}, 'US States')

# Create a collection with fromImages().
#collectionFromImages = ee.ImageCollection.fromImages(
#  [ee.Image(3), ee.Image(4)])
"""

# Merge two collections.
#mergedCollection = collectionFromConstructor.merge(collectionFromImages)
#print('mergedCollection: ', mergedCollection.getInfo())

# Use a Polygon


# Get the QBD surface > X over the polygon



