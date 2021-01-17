#from getoutlook import getDates
import fiona, os
import matplotlib.pyplot as plt
import cartopy
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

"""
Notes:
        - The "DN" attribute in each of the outlook shapefiles refers to the layer's severe category. 
          As far as I can tell, the order goes: 
                                        DN 2 = General Thunder
                                        DN 3 = Marginal
                                        DN 4 = Slight
                                        DN 5 = Enhanced
                                        DN 6 = Moderate
                                        DN 7 = High
        - Note that there is sometimes a second DN 2 layer that has like  points. I'm not sure what this is, but it 
          is not the actual general thunder area. 
"""

# Laptop
# DataDirectory = 'C:\\Users\\admoo\\Desktop\\Projects\\FalseAlarm\\csv\\'
# Shapefiles = 'C:\\Users\\admoo\\Desktop\\Projects\\FalseAlarm\\outlooks\\'
# outdir = 'C:\\Users\\admoo\\Desktop\\Projects\\FalseAlarm\\outlooks\\'
# WARfilename = 'ConWarnings_2015_2018.csv'

# home PC
DataDirectory = 'H:\\Research\\FalseAlarm\\csv\\'
Shapefiles = 'H:\\Research\\FalseAlarm\\outlooks\\day1otlk_20160614_1300\\'
outdir = 'H:\\Research\\FalseAlarm\\outlooks\\'
WARfilename = 'ConWarnings_2015_2018.csv'


testdates = ["20160517","20170314"]

def plotShapefile(shpfile):

    ax = plt.axes(projection=ccrs.PlateCarree())
    shape_feature = ShapelyFeature(Reader(shpfile).geometries(),
                                   ccrs.PlateCarree(),
                                   facecolor='none',
                                   edgecolor='b')
    ax.add_feature(shape_feature)
    ax.coastlines()
    ax.add_feature(cartopy.feature.BORDERS)
    ax.add_feature(cartopy.feature.STATES)
    ax.set_extent([-125,-60,20,50])
    plt.show()
    # One trick may be to convert the current shape file to a different
    # reference/geographic system using shpproj from shapelib. 

def readShapefile(shpfile):
    print(shpfile)
    print("")
    shape = fiona.open(shpfile)
    #print(shape.schema)
    for feat in shape:
        #print(feat)
        print(feat['properties']['DN'])
        print(len(feat['geometry']['coordinates'][0]))
        print("")
    plotShapefile(shpfile)


# for date in testdates:
#     shapefile_dir = "day1otlk_" + date + "_1300\\"
#     shpfile = "day1otlk_" + date + "_1300_hail.shp"
#     readShapefile(Shapefiles+shapefile_dir+shpfile)

readShapefile(Shapefiles+"day1otlk_20160614_1300_cat.shp")