"""
Testing the bits description of clouds in Landsat in order to compare
"""
import ee
import geemap
from datetime import datetime
import numpy as np
ee.Initialize()
from library import get_valid_date, get_image_Landsat8, get_region, get_surface, get_surface_feature

threshold = 0.05

######
# ALGORITHM Cloud detection
# For LANDSAT, applied to TOA

######
# (Tile 229081)
collection = ee.ImageCollection("LANDSAT/LC08/C01/T1_TOA")
coll = collection.filter(ee.Filter.eq('WRS_PATH', 229)).filter(ee.Filter.eq('WRS_ROW', 81));
dates, score = get_valid_date(coll)
#save the dates with a score higher than the threshold
retain229081 = [dates[i] for i in range(len(dates)) if score[i]<threshold] 
retainscore229081 = [score[i] for i in range(len(dates)) if score[i]<threshold] 

######
# (Tile 228081)
collection = ee.ImageCollection("LANDSAT/LC08/C01/T1_TOA")
coll = collection.filter(ee.Filter.eq('WRS_PATH', 228)).filter(ee.Filter.eq('WRS_ROW', 81));
dates, score = get_valid_date(coll)
#save the dates with a score higher than the threshold
retain228081 = [dates[i] for i in range(len(dates)) if score[i]<threshold] 
retainscore228081 = [score[i] for i in range(len(dates)) if score[i]<threshold] 

##############################

def maskL8toa(img):
  cloudsBitMask = (1 << 4)
  qa = img.select('BQA')
  mask = qa.bitwiseAnd(cloudsBitMask).eq(0)
  return mask

collection = ee.ImageCollection("LANDSAT/LC08/C01/T1_TOA")
coll = collection.filter(ee.Filter.eq('WRS_PATH', 228)).filter(ee.Filter.eq('WRS_ROW', 81))
coll = coll.map(maskL8toa)
coll = coll.map(get_surface_feature)
A = coll.getInfo()
# I set a threshold of 0.77 (from what I saw..)
A = {a['id'][-8:]:a['properties']["clouds"] for a in A["features"] if a['properties']["clouds"] >0.77}

for k in A.keys():
  print(k, A[k])

print(retain228081)

