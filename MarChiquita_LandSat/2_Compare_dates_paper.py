"""
This script is used to show specific dates
It is used to evaluate the different date used exclusively
in the paper and exclusively in our results 
"""
############
# Library
import ee
import geemap
from datetime import datetime
import numpy as np
ee.Initialize()
from library import get_region

def get_image(dd):
   """
   dd is a two element list
   First element  - tile 228
   Second element - tile 229
   """
   d1 = dd[0]; d2 = dd[1]
   im = "LANDSAT/LC08/C01/T1_SR/LC08_{0}_{1}".format(d1, d2)
   IMAGE = ee.Image(im)
   return IMAGE

region = get_region()
   
Dates = {}
Dates["CASE 1 - a"] = ["228081", "20140122"]
Dates["CASE 1 - b"] = ["228081", "20140106"]
Dates["CASE 1"]     = ["229081", "20140113"]

Dates["CASE 2-228"] = ["228081", "20150906"]
Dates["CASE 2-229"] = ["229081", "20150913"]

Dates["CASE 3"]     = ["229081", "20170411"]
Dates["CASE 3 - a"] = ["228081", "20170319"]
Dates["CASE 3 - b"] = ["228081", "20170420"]


m = geemap.Map(location=[-30, -64], zoom_start=8)
for d in Dates.keys():
    IMAGE = get_image(Dates[d]) 
    m.addLayer(IMAGE, {"bands": ['B4', 'B3', 'B2'], "min": 0, "max": 2000}, d)
m.addLayer(region, {}, 'Polygon')
m.save('./Output/2_Cases.html')
