import ee
import geemap
from datetime import datetime
import numpy as np
ee.Initialize()
from library import get_valid_date, get_image_Landsat8, get_region

######

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

# Group valid dates which are closed

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
        Lscore.append([score2[l], score1[i]])

for l,s in zip(Ldates, Lscore):
   print("*")
   print("{0}: {1}".format(l[0], s[0]))
   print("{0}: {1}".format(l[1], s[1]))

#####################
# MAP everything
region = get_region()

m = geemap.Map(location=[-30, -64], zoom_start=8)
for i,dd in enumerate(Ldates):
    print("{0}/{1}".format(i, len(Ldates)) )
    IMAGE = get_image_Landsat8(dd)
    name = "{0}: {1}-{2} ({3},{4})".format(i,dd[0],dd[1],Lscore[i][0],Lscore[i][1])
    m.addLayer(IMAGE, vis_params = {"bands": ['B4', 'B3', 'B2'], "min": 0, "max": 2000}, name = name, shown = False)
m.addLayer(region, {}, 'Polygon', opacity = 0.5,shown = False)
m.save('./Output/1_retained_dates.html')

#####################

# From the map we can make a list of the date index to be removed
exclusion = [15,14,10]

# This is for another script, in order not to copy manually
# In 4_Calcul_Final.py
for k, dd in enumerate(Ldates):
    d229 = dd[0]; d228 = dd[1]
    if k not in exclusion:
        print("Dpair['{0}'] = get_pair('{0}', '{1}')".format(d229, d228))
        
