import ee
import geemap
from datetime import datetime
import numpy as np
import json
ee.Initialize()


def addmNDWI(image):
  mNDWI = image.normalizedDifference(['Nadir_Reflectance_Band4', 'Nadir_Reflectance_Band6']).rename('mNDWI');
  return image.addBands(mNDWI)
  
def getMaskQual(image):
   var= "BRDF_Albedo_Band_Mandatory_Quality_Band{}"
   immask6 = image.select(var.format(6)).unmask(1000)
   immask4 = image.select(var.format(4)).unmask(1000)
   immask = immask6.eq(1000).Or(immask4.eq(1000)).rename("Mask")
   return immask
   
def get_surface(img):
   areaImage = img.multiply(ee.Image.pixelArea())
   stats = areaImage.reduceRegion(reducer =  ee.Reducer.sum(),\
      geometry = marChiquita,\
      scale= 30,\
      maxPixels= 1e9)
   return stats

def get_mask_feature(img):
    date = img.get('date');
    mask = get_surface(img.select(["Mask"]));
    #
    ft = ee.Feature(None, {
        'date': date,\
        'mask': ee.Number( mask.get("Mask")).divide(marChiquita.area()) .multiply(100)
        }
        )
    return ft

def convert_date(d):
    d0 = datetime.strptime(d, '%Y/%m/%d').date()
    return d0   

def flood_mask(image):
  mndwi = image.select(['mNDWI']);
  noflood =  mndwi.lt(-0.35).rename('noflood');
  partflood =  mndwi.lt(0.4).And(mndwi.gt(-0.35)).rename('pflooded');
  fullflood = mndwi.gt(0.4).rename('flooded')
  im = image.addBands(partflood)
  im = im.addBands(fullflood)
  im = im.addBands(noflood)
  return im

def get_flood_feature(img):
    date = img.get('date');
    flooded_surf = get_surface(img.select(["flooded"]));
    part_flooded = get_surface(img.select(["pflooded"]));
    noflood =      get_surface(img.select(["noflood"]));
    #
    ft = ee.Feature(None, {'date': date,\
            'flooded': ee.Number(flooded_surf.get('flooded')).divide(1000*1000),\
            'part_flooded': ee.Number(part_flooded.get('pflooded')).divide(1000*1000),\
            #'noflood' : ee.Number(noflood.get('noflood')).divide(1000*1000)\
            })
    return ft
  
#########################   

f = "/home/anthony/Documents/Doctorat/PROD/Floodedmap/MARCHIQUITA.json"
with open(f) as json_file:
    data = json.load(json_file)
marChiquita = ee.Geometry.Polygon(data["coordinates"])
    
# REPRENDRE MAIS AVEC 16 days PRODUCT    
"""    
coll = ee.ImageCollection("MODIS/006/MCD43A4")
Q = coll.filterBounds(marChiquita).filterDate('2013-01-01', '2014-01-01').select(["BRDF_Albedo_Band_Mandatory_Quality_Band6", "BRDF_Albedo_Band_Mandatory_Quality_Band4"])

maskcoll = Q.map(getMaskQual)
fmask = maskcoll.map(get_mask_feature)

print(fmask.getInfo())
taskParams = {
    'driveFolder': '',
    'fileFormat': 'CSV'   # CSV, KMZ, GeoJSON
}

# export all features in a FeatureCollection as one file
task = ee.batch.Export.table(fmask, 'export_fc', taskParams)
task.start()
"""

coll = ee.ImageCollection("MODIS/006/MCD43A4")
coll = coll.filterBounds(marChiquita).filterDate('2013-01-01', '2013-01-15')

im = coll.mosaic()
im = addmNDWI(im)
viz = {"min":0, "max":3000,"bands":["Nadir_Reflectance_Band1","Nadir_Reflectance_Band4","Nadir_Reflectance_Band3"]};
im = flood_mask(im)
ft = get_flood_feature(im)


m = geemap.Map(location=[-30, -64], zoom_start=8)
m.addLayer(im, viz, "Real Color")
m.addLayer(im, {"min":-1, "max":1,"bands":['mNDWI']}, "mNDWI")
m.addLayer(im, {"min":0, "max":1,"bands":['flooded']}, "flood")
m.addLayer(im, {"min":0, "max":1,"bands":["pflooded"]}, "pflood")
m.save('./Output/MCD43A4.html')

