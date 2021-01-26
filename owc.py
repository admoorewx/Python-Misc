#from getoutlook import getDates
import csv, os
import fiona
import requests
import zipfile
import pyproj
import cartopy
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
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
Shapefiles = 'H:\\Research\\FalseAlarm\\outlooks\\shapefiles\\'
outdir = 'H:\\Research\\FalseAlarm\\outlooks\\shapefiles\\'
indir = 'H:\\Research\\FalseAlarm\\outlooks\\'
WARfilename = 'ConWarnings_2015_2018.csv'


def getDates(DataDirectory,filename):
    print("Processing file: " + DataDirectory + filename+"\n")
    output = []
    os.chdir(DataDirectory)
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row[2][0:-4] in output:
                pass
            else:
                output.append(row[2][0:-4])
    csv_file.close()
    return output


def getOutlook(date,indir):
    print("     Retreiving File...")
    try:
        year = date[0:4]
        url = "https://www.spc.noaa.gov/products/outlook/archive/"+year+"/day1otlk_"+date+"_1300-shp.zip"
        savename = "day1otlk_"+date+"_1300-shp.zip"
        r = requests.get(url)
        with open(indir+savename,'wb') as f:
            f.write(r.content)
        print("     Retrieved file "+savename)
        return savename
    except:
        print("     Retrieval failed!")
        exit()

def unzip(zfile,indir,outdir):
    """
    Unzips a zip file. Not very robust yet.
    :param zfile: name of the .zip file you want to unzip
    :param indir: location where the .zip file is located.
    :param outdir: location where you want the contents to go.
    :return: nothing. Just unzips the .zip contents.
    """
    try:
        inpath = indir+zfile[0:-8]
        outpath = outdir
        #os.mkdir(inpath)
        with zipfile.ZipFile(indir+zfile,'r') as zip_ref:
            zip_ref.extractall(outpath)
        print("     Unzipped file "+zfile+"\n")
    except:
        print("     Unzipping failed!")
        exit()

def plotShapefile(shpfile,datestring,polygon=None):
    """
    Plots an SPC outlook for a given day.
    :param shpfile: shapefile for the SPC outlook.
    :param datestring: String of the date the outlook is valid for (in YYYYMMDD format).
    :return: plots a nice image. (Well, maybe not that nice...)
    """

    lambproj = ccrs.LambertConformal(central_longitude=0,
                                     central_latitude=0,
                                     standard_parallels=(33,45))

    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()
    ax.add_feature(cartopy.feature.BORDERS)
    ax.add_feature(cartopy.feature.STATES)

    for record in Reader(shpfile).records():
        category = record.attributes['DN']
        colors = ["lightgreen","g","yellow","orange","r","magenta"]
        ecolors = ["k","g","gold","darkorange","r","purple"]
        lwidth = 1
        if category == 2:
            ax.add_geometries([record.geometry],crs=lambproj,edgecolor=ecolors[0],facecolor=colors[0],linewidth=lwidth,alpha=0.35)
        if category == 3:
            ax.add_geometries([record.geometry],crs=lambproj,edgecolor=ecolors[1],facecolor=colors[1],linewidth=lwidth,alpha=0.5)
        if category == 4:
            ax.add_geometries([record.geometry],crs=lambproj,edgecolor=ecolors[2],facecolor=colors[2],linewidth=lwidth,alpha=0.5)
        if category == 5:
            ax.add_geometries([record.geometry],crs=lambproj,edgecolor=ecolors[3],facecolor=colors[3],linewidth=lwidth,alpha=0.5)
        if category == 6:
            ax.add_geometries([record.geometry],crs=lambproj,edgecolor=ecolors[4],facecolor=colors[4],linewidth=lwidth,alpha=0.5)
        if category == 8:
            ax.add_geometries([record.geometry],crs=lambproj,edgecolor=ecolors[5],facecolor=colors[5],linewidth=lwidth,alpha=0.5)


    if polygon is not None:
        ax.add_geometries([polygon], crs=ccrs.PlateCarree(), edgecolor='red', facecolor='none', linewidth=3, alpha=0.5,
                          zorder=10)
        x, y = polygon.centroid.coords.xy
        #ax.plot(x[0],y[0],'ko',markersize=5, transform=ccrs.PlateCarree())
        ax.text(x[0],(y[0]+0.5),'Warning',transform=ccrs.PlateCarree())
        buffer = 2.0  # degrees
        # print(center.xy[0][0],center.xy[1][0])
        left_lon = x[0] - buffer
        right_lon = x[0] + buffer
        top_lat = y[0] + buffer
        bottom_lat = y[0] - buffer
        ax.set_extent((left_lon, right_lon, bottom_lat, top_lat))
    else:
        ax.set_extent([-128, -65, 23, 48])

    plt.title("SPC 1300 UTC Convective Outlook on "+datestring)
    plt.show()
    plt.clf()


def getShapefile(datestring,Shapefiles=None,indir=None):
    """
    Returns a shapefile of the SPC outlook for the date requested.
    :param datestring: A string that is in YYYYMMDD format
    :param Shapefiles: Path to the directory that is housing the shapefiles
    :param indir: Path to the directory where the subroutine getOutlook will place the downloaded shapefile
    :return: returns the path to the requested shapefile. If the file is not found nor retrieved then an
             error message is displayed.
    """
    if Shapefiles is None:
        Shapefiles = 'H:\\Research\\FalseAlarm\\outlooks\\shapefiles\\'
    if indir is None:
        indir = 'H:\\Research\\FalseAlarm\\outlooks\\'

    # Datestring needs to be in YYYYMMDD format
    datestring = datestring + "_1300"
    shpfile = "day1otlk_"+datestring+"_cat.shp"
    try:
        print("     Outlook retrieved!")
        return os.path.join(Shapefiles,shpfile)
    except:
        try:
            print("     Trying to get new outlook for date "+datestring)
            filename = getOutlook(datestring,indir)
            unzip(filename,indir,Shapefiles)
            print("     Outlook retrieved!")
            return os.path.join(Shapefiles, shpfile)
        except:
            print("ERROR: Could not find nor retrieve the requested outlook shapefile!")
            return None

def changeProjection(polygon):
    x,y = polygon.exterior.coords.xy
    # +ellps=WGS84 +datum=WGS84
    projection = pyproj.Proj("+proj=lcc +lat_1=33 +lat_2=45 ellps=GRS80 +units=m")
    lon,lat = projection(x,y,inverse=True)
    points = []
    for l,L in enumerate(lat):
        points.append([lon[l],L])
    new_polygon = Polygon(points)
    return new_polygon


def getWarnCat(warning,outlook):
    """
    :param warning: the warning polygon (A Shapely Polygon object).
    :param outlook: the SPC outlook shapefile.
    :return: returns the category that the center point of the warning was in at the time of issuance.
            Note: More specifically, this returns the DN number that corresponds to the appropriate category.
            The DN convection follows: 2 = Gen Thunder, 3 = Marginal, 4 = Slight, 5 = Enhanced, 6 = Moderate, 8 = High.
            Why is there no DN = 7? I have no idea. (Pfff, government work!)
    """
    warning_center = warning.centroid # gives Shapely Point object
    cats = []
    for record in Reader(outlook).records():
        category = record.attributes['DN']
        cat_poly = record.geometry
        cat_poly = changeProjection(cat_poly)
        if cat_poly.contains(warning_center) or warning_center.within(cat_poly):
            cats.append(category)
        else:
            continue
    if len(cats) == 0:
        return 0 # return a zero for no category
    else:
        return max(cats)

