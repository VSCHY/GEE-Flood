import ee
import geemap
from datetime import datetime
import numpy as np
ee.Initialize()

##############################
# Exclusive Landsat

import json
f = "../MARCHIQUITA.json"
with open(f) as json_file:
    data = json.load(json_file)
# This one is geodesic 
region = ee.Geometry.Polygon(data["coordinates"])

def get_region():
   return region

def addMaskCloud(image):
   cloud = ee.Algorithms.Landsat.simpleCloudScore(image).select('cloud')
   clouds = cloud.rename('CLOUDS');
   clouds = clouds.gt(90).rename('CLOUDS');
   im = image.addBands(clouds)
   return im

def get_cloud_feature(img):
    date = img.get('system:time_start');
    stats = get_surface(img.select("CLOUDS")).get("CLOUDS")
    ft = ee.Feature(None, {'date': ee.Date(date).format('Y/M/d'), 
            'cloudRegion': ee.Number(stats).divide(region.area()).multiply(100),
    });
    return ft

def get_image_Landsat8(dd):
   d2 = dd[0]; d1 = dd[1]
   im1 = "LANDSAT/LC08/C01/T1_SR/LC08_228081_{0}".format(d1)
   im2 = "LANDSAT/LC08/C01/T1_SR/LC08_229081_{0}".format(d2)
   IMAGE = ee.ImageCollection.fromImages([ee.Image(im1), ee.Image(im2)]).median()
   return IMAGE

def get_valid_date(coll):
   cl = coll.map(addMaskCloud)
   cl = cl.select("CLOUDS")
   clstat = cl.map(get_cloud_feature)
   stat = clstat.getInfo()
   #
   dates = [convert_date(s["properties"]['date']) for s in stat["features"]]
   score = [s["properties"]['cloudRegion'] for s in stat["features"]]
   #
   return dates, score


##############################

def get_surface(img):
   areaImage = img.multiply(ee.Image.pixelArea())
   stats = areaImage.reduceRegion(reducer =  ee.Reducer.sum(),\
      geometry = region,\
      scale= 30,\
      maxPixels= 1e9)
   return stats

def get_surface_feature(img):
    stats = get_surface(img)
    #
    date = img.get('system:time_start')
    ft = ee.Feature(None, {'date': date,\
            'clouds': ee.Number(stats.get('BQA')).divide(region.area())
            })
    return ft 

def convert_date(d):
    d0 = datetime.strptime(d, '%Y/%m/%d').date()
    return d0   

##############################

def addmNDWI(image):
  mNDWI = image.normalizedDifference(['B3', 'B6']).rename('mNDWI');
  return image.addBands(mNDWI)

def flood_mask(image):
  mndwi = image.select(['mNDWI']);
  noflood =  mndwi.lt(-0.35).rename('noflood');
  partflood =  mndwi.lt(0.5).And(mndwi.gt(-0.35)).rename('pflooded');
  fullflood = mndwi.gt(0.5).rename('flooded')
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
    
def get_image(pair):
   im1 = "LANDSAT/LC08/C01/T1_SR/LC08_{0}_{1}".format("228081", pair["228081"])
   im2 = "LANDSAT/LC08/C01/T1_SR/LC08_{0}_{1}".format("229081", pair["229081"])
   img = ee.ImageCollection.fromImages([ee.Image(im1), ee.Image(im2)]).median()
   # Need to ad an id
   img = img.setMulti({"date": pair["228081"]})
   # Need to convert it to an image again
   return ee.Image(img)
  
