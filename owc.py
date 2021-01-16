from getoutlook import getDates
import fiona
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

# Laptop
DataDirectory = 'C:\\Users\\admoo\\Desktop\\Projects\\FalseAlarm\\csv\\'
Shapefiles = 'C:\\Users\\admoo\\Desktop\\Projects\\FalseAlarm\\outlooks\\'
outdir = 'C:\\Users\\admoo\\Desktop\\Projects\\FalseAlarm\\outlooks\\'
WARfilename = 'ConWarnings_2015_2018.csv'

testdates = ["20160517","20170314"]

def plotShapefile(shpfile):

    ax = plt.axes(projection=ccrs.PlateCarree())
    shape_feature = ShapelyFeature(Reader(shpfile).geometries(),
                                   ccrs.PlateCarree(),
                                   facecolor='k',
                                   edgecolor='k')
    ax.add_feature(shape_feature)
    ax.coastlines()
    ax.set_extent([-125,-60,20,50])
    plt.show()
    # One trick may be to convert the current shape file to a different
    # reference/geographic system using shpproj from shapelib. 

def readShapefile(shpfile):
    print(shpfile)
    print("")
    shape = fiona.open(shpfile)
    #print(shape.schema)
    first = next(iter(shape))
    for key,value in first.items():
        #print(value)
        try:
            for k,v in value.items():
                print(k,v)
        except:
            continue
    plotShapefile(shpfile)


for date in testdates:
    shapefile_dir = "day1otlk_" + date + "_1300\\"
    shpfile = "day1otlk_" + date + "_1300_hail.shp"
    readShapefile(Shapefiles+shapefile_dir+shpfile)