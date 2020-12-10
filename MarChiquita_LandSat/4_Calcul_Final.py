"""
Make the surface calculation for all "our" valid dates pair.
"""
import ee
import geemap
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
ee.Initialize()
from library import get_region, get_image, addmNDWI, flood_mask,get_flood_feature, get_surface
from matplotlib.dates import  DateFormatter
import matplotlib.dates as mdates

def get_pair(d1, d2):    
   pair = {}
   pair["228081"] = d2
   pair["229081"] = d1
   return pair

region = get_region()
   
# Valid dates (from the 1_Cloudless_dates.py)
Dpair = {}   
Dpair['20130416'] = get_pair('20130416', '20130425')
Dpair['20130619'] = get_pair('20130619', '20130612')
Dpair['20140419'] = get_pair('20140419', '20140412')
Dpair['20141012'] = get_pair('20141012', '20141021')
Dpair['20150201'] = get_pair('20150201', '20150125')
Dpair['20151116'] = get_pair('20151116', '20151109')
Dpair['20170411'] = get_pair('20170411', '20170420')
Dpair['20170902'] = get_pair('20170902', '20170911')
Dpair['20170918'] = get_pair('20170918', '20170911')
Dpair['20171105'] = get_pair('20171105', '20171114')
Dpair['20181108'] = get_pair('20181108', '20181117')
Dpair['20181210'] = get_pair('20181210', '20181203')
Dpair['20190228'] = get_pair('20190228', '20190221')
Dpair['20191127'] = get_pair('20191127', '20191206')
Dpair['20200114'] = get_pair('20200114', '20200107')
Dpair['20200302'] = get_pair('20200302', '20200224')
Dpair['20200403'] = get_pair('20200403', '20200412')
Dpair['20200419'] = get_pair('20200419', '20200412')

#########
# MAP All the images and their corresponding mNDWI
m = geemap.Map(location=[-30, -64], zoom_start=8)
for i,k in enumerate(Dpair.keys()):
    IMAGE = get_image(Dpair[k])
    IMAGE = addmNDWI(IMAGE)
    si = str(i)+". "
    m.addLayer(IMAGE, {"bands": ['B4', 'B3', 'B2'], "min": 0, "max": 2000}, si+k, shown = False)
    m.addLayer(IMAGE, {"bands": ['mNDWI'], "min": -1, "max": 1}, si+"mNDWI {0}".format(k), shown = False)
m.addLayer(region, {}, 'Polygon', opacity = 0.5, shown = False)
m.save('./Output/4_Valid_Dates.html')


#########
# Calculation
IMLIST = []
for k in Dpair.keys():
    pair = Dpair[k]
    IMLIST.append(get_image(pair))  
ImColl = ee.ImageCollection.fromImages(IMLIST)
ImColl = ImColl.map(addmNDWI)
ImColl = ImColl.map(flood_mask)
ft = ImColl.map(get_flood_feature)

#########
# Prepare plot
ft = ft.getInfo()
date = [ft["features"][i]["properties"]["date"] for i in range(len(ft["features"]))]
date1 = [datetime.strptime(d, '%Y%m%d').date() for d in date]
flood1 = [f["properties"]["flooded"] for f in ft["features"]]
pflood1 = [f["properties"]["part_flooded"] for f in ft["features"]]
tot1 = np.array(flood1)+np.array(pflood1)

# PLOT
plt.plot_date(date1, flood1, ls = "-", label = "open-water")
plt.plot_date(date1, pflood1, ls = "-", label = "mixed-water")
plt.plot_date(date1, tot1, ls = "-", label = "total")
plt.ylim(0,5000)
ax = plt.gca()
ax.xaxis.set_major_formatter( DateFormatter('%Y-%m') )
ax.xaxis.set_major_locator(mdates.YearLocator(1,month=1,day = 1))
ax.set_xlim(datetime(2013, 1, 1), datetime(2018, 1, 1))

plt.legend()
plt.savefig("./Output/4_Final_TimeSerie.png", dpi = 300)






