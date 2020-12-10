"""
This script is used to make the calculation of the region
using the same date as the paper
"""
############
# Library
import ee
import geemap
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
ee.Initialize()
from library import get_region, get_image, addmNDWI, flood_mask,get_flood_feature
from matplotlib.dates import  DateFormatter
import matplotlib.dates as mdates

region = get_region()

def get_pair(d1, d2):    
   pair = {}
   pair["228081"] = d2
   pair["229081"] = d1
   return pair

# Each Dpair element is an prepare a dictionnary 
# of the date for the two tiles
Dpair = {}   
Dpair["20130416"] = get_pair("20130416", "20130425")
Dpair["20140113"] = get_pair("20140113", "20140122")
Dpair["20150913"] = get_pair("20150913", "20150906")
Dpair["20160204"] = get_pair("20160204", "20160229")
Dpair["20170411"] = get_pair("20170411", "20170319")
Dpair["20170918"] = get_pair("20170918", "20170911")

# The element of Dpair are merged through get_image and added to the 
# IMLIST
IMLIST = []
for k in Dpair.keys():
    print(k)
    pair = Dpair[k]
    print(pair)
    IMLIST.append(get_image(pair))  

# We create an ImageCollection from IMLIST and then process the images
ImColl = ee.ImageCollection.fromImages(IMLIST)
ImColl = ImColl.map(addmNDWI)
ImColl = ImColl.map(flood_mask)
ft = ImColl.map(get_flood_feature)

# To get the results and prepare the data to plot it
ft = ft.getInfo()
date = [ft["features"][i]["properties"]["date"] for i in range(len(ft["features"]))]
date1 = [datetime.strptime(d, '%Y%m%d').date() for d in date]
#
flood = [f["properties"]["flooded"] for f in ft["features"]]
pflood = [f["properties"]["part_flooded"] for f in ft["features"]]
tot = np.array(flood)+np.array(pflood)
#
# PLOT
plt.plot_date(date1, flood, ls = "-", label = "open-water")
plt.plot_date(date1, pflood, ls = "-", label = "mixed-water")
plt.plot_date(date1, tot, ls = "-", label = "total")
ax = plt.gca()
ax.xaxis.set_major_formatter( DateFormatter('%Y-%m') )
ax.xaxis.set_major_locator(mdates.YearLocator(1,month=1,day = 1))
ax.set_xlim(datetime(2013, 1, 1), datetime(2018, 1, 1))

plt.ylim(0,5000)
plt.legend()
plt.savefig("./Output/3_same date.png", dpi = 300)

