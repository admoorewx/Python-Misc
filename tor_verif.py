import os
import csv
import datetime
import numpy as np
from ast import literal_eval
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import cartopy.io.shapereader as shpreader
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from owc import getShapefile,getWarnCat,plotShapefile

DataDirectory = 'H:\\Research\\FalseAlarm\\csv\\' # Path to where your data is stored
outdir = 'H:\\Research\\FalseAlarm\\images\\' # directory where you want output images to be saved to
WARfilename = 'ConWarnings_2015_2018.csv'
LSRfilename = '2015_2018_tor.csv'


def dataReadIn(DataDirectory,filename):
    print("Processing file: " + DataDirectory + filename+"\n")
    output = []
    os.chdir(DataDirectory)
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if len(row) > 0:
                output.append(row)
    csv_file.close()
    return output

def getTornadoTimesList(Tornadoes):
    times = []
    for tornado in Tornadoes:
        timezone = tornado[6]
        if timezone != "?":
            yearmonthday = tornado[1] + tornado[2] + tornado[3]
            time = datetime.datetime.strptime(yearmonthday+tornado[5], "%Y%m%d%H:%M:%S")
            if timezone == "3":
                # Convert from central to UTC
                time = time + datetime.timedelta(hours=6)
            times.append(time)
        else:
            times.append(np.nan) # We need this here to hold the location and more easily match the tornado time with the tornado later on.
    return times

def createPath(beginPoint,endPoint,incr):
    # function returns a 2-D array of points along a straight line
    # beginning at "beginPoint" and ending at "endPoint".
    # beginPoint and endPoint are both lat/lon pairs within an array
    # (i.e. [34.4,-96.5]). incr is the increment (in degrees) between each
    # new point along the line that is created.
    deltax = (endPoint[1]-beginPoint[1])/incr
    deltay = (endPoint[0]-beginPoint[0])/incr
    try:
        xs = np.arange(beginPoint[1],endPoint[1],deltax)
        ys = np.arange(beginPoint[0],endPoint[0],deltay)
        return [xs,ys]
    except:
        print(" Warning: possible single point tornado.")
        #print(deltax,deltay)
        #print(beginPoint,endPoint)
        return [[beginPoint[1]],[beginPoint[0]]]

def plotWarnAndPath(path,polygon,torTime,warnTime,WFO,outdir):
    # plot a warning polygon as well as the path points
    # first let's color code the path points based on whether or not they're in
    # the warning polygon
    colors = []
    lats = path[1]
    lons = path[0]
    for loc,lat in enumerate(lats):
        #print(lat,lons[loc])
        point = Point(float(lons[loc]), float(lat))
        if (polygon.contains(point) or (point.within(polygon))):
            colors.append('g')
        else:
            colors.append('darkslateblue')

    center = polygon.centroid
    buffer = 1.0 #degrees
    #print(center.xy[0][0],center.xy[1][0])
    left_lon = center.xy[0][0] - buffer
    right_lon = center.xy[0][0] + buffer
    top_lat = center.xy[1][0] + buffer
    bottom_lat = center.xy[1][0] - buffer

    # Read in the state shapefiles
    #state_reader = shpreader.Reader('H:/Python/shapefiles/ne_10m_admin_1_states_provinces.shp')
    #good_states = list(state_reader.geometries())
    #GOOD_STATES = cfeature.ShapelyFeature(good_states, ccrs.PlateCarree())
    # Read in the county shapefiles
    reader = shpreader.Reader('H:/Python/shapefiles/tl_2017_us_county.shp')
    counties = list(reader.geometries())
    COUNTIES = cfeature.ShapelyFeature(counties, ccrs.PlateCarree())

    # Create the figure
    fig = plt.figure(1, figsize=(8, 9))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.background_patch.set_facecolor('lightsteelblue')

    #ax.add_feature(cfeature.COASTLINE.with_scale('50m'), zorder=1)
    ax.add_feature(COUNTIES, facecolor='lightgray', edgecolor='k', alpha=0.9, zorder=2)
    #ax.add_feature(GOOD_STATES, facecolor='lightgray', edgecolor='k', alpha=0.9, zorder=3)
    ax.add_feature(cfeature.LAKES, facecolor='lightsteelblue', alpha=0.95, zorder=4)
    ax.set_extent((left_lon, right_lon, bottom_lat, top_lat))

    # add the polygon
    ax.add_geometries([polygon], crs=ccrs.PlateCarree(), edgecolor='red', facecolor='none', linewidth=3, alpha=0.5, zorder=10)

    #plot the points along the path
    # print(left_lon,right_lon)
    # print(lons)
    # print(lats)
    plt.scatter(x=lons, y=lats,
                c=colors,
                alpha=0.75,
                zorder=10,
                transform=ccrs.PlateCarree())  ## Important

    xlabel = "Nearby Tornado Occurrence at: "+torTime+".\n Began Near: "+str(round(path[1][0],2))+", "+str(round(path[0][0],2))+"\n Ended Near: "+str(round(path[1][-1],2))+", "+str(round(path[0][-1],2))
    plt.title("Tor Warning from WFO " + WFO + "\n issued at " + warnTime)
    ax.text(0.5, -0.1, xlabel, va='bottom', ha='center',
            rotation='horizontal', rotation_mode='anchor',
            transform=ax.transAxes)

    saveDate = datetime.datetime.strptime(warnTime,"%Y-%m-%d %H:%M:%S")
    saveTime = datetime.datetime.strftime(saveDate,"%y%m%d_%H%M")

    #plt.show()
    plt.savefig(outdir+WFO+"_"+saveTime+".png")
    plt.clf()

def createPolygon(verticies):
    points = []
    verticies = literal_eval(verticies) # This takes care of converting the array-string into just an array
    for pair in verticies:
        (lon, lat) = pair
        point = [lon,lat]
        points.append(point)
    points = np.asarray(points)
    polygon = Polygon(points)
    return polygon

def getCat(Warning,outlook,plot=False,date=None):
    try:
        polygon = createPolygon(Warning[4])
    except:
        polygon = createPolygon(Warning[4][0])

    if plot:
        plotShapefile(outlook,date,polygon)

    print("     Trying to get category")
    DN = getWarnCat(polygon,outlook)
    print("     Category retrieved.")
    if DN == 0:
        return "NON"
    elif DN == 2:
        return "GNT"
    elif DN == 3:
        return "MGL"
    elif DN == 4:
        return "SLT"
    elif DN == 5:
        return "ENH"
    elif DN == 6:
        return "MOD"
    elif DN == 8:
        return "HIG"
    else:
        print("Category could not be determined!")
        return None

def checkForLSR(Warning,Tornadoes,TorTimes):
    # This function takes in a single warning and checks the list of tornado times and occurrences to
    # see if a tornado occurred in the warning polygon. The tornado list if first filtered by date/time, then
    # a spatial check is performed. If a tornado occurrenced happened on the warning day and within the warning polygon
    # then verified = True is returned. Otherwise verified = False.
    beginTime = datetime.datetime.strptime(Warning[2],"%Y%m%d%H%M")
    endTime = datetime.datetime.strptime(Warning[3],"%Y%m%d%H%M")
    TorTimes = np.asarray(TorTimes)


    verified = False

    for T, torTime in enumerate(TorTimes):
        if torTime.year == beginTime.year or torTime.year == endTime.year: # Check year
            if torTime.month == beginTime.month or torTime.month == endTime.month: # check month
                if torTime.day == beginTime.day or torTime.day == endTime.day: # check day
                    if torTime.hour == beginTime.hour or torTime.hour == endTime.hour: # check hour

                        print("Tornado Occurred on this day.")

                        # Now check for a tornado within the polygon
                        # We'll try two ways since sometimes the list of coords was embedded within a larger list of length 1.
                        try:
                            polygon = createPolygon(Warning[4])
                        except:
                            polygon = createPolygon(Warning[4][0])

                        # get the tornado begin and end points, as well as the tornado time and warning time.
                        beginPoint = Point(float(Tornadoes[T][16]), float(Tornadoes[T][15])) # Note that Point takes lon, lat pair
                        endPoint = Point(float(Tornadoes[T][18]), float(Tornadoes[T][17]))
                        torTime = datetime.datetime.strftime(TorTimes[T],"%Y-%m-%d %H:%M:%S")
                        warnTime = datetime.datetime.strftime(beginTime,"%Y-%m-%d %H:%M:%S")

                        # Check for the begin/end points first
                        if (polygon.contains(beginPoint) or (beginPoint.within(polygon))):
                            print(" Tornado found!")
                            # Plot the warning
                            start = [float(Tornadoes[T][15]), float(Tornadoes[T][16])]
                            end = [float(Tornadoes[T][17]), float(Tornadoes[T][18])]
                            path = createPath(start, end, 10.0)
                            plotWarnAndPath(path, polygon, torTime, warnTime, Warning[0], outdir)
                            return True

                        # If that didn't work, then check the end point
                        elif (polygon.contains(endPoint) or (endPoint.within(polygon))):
                            print(" Tornado found!")
                            # Plot the warning
                            start = [float(Tornadoes[T][15]), float(Tornadoes[T][16])]
                            end = [float(Tornadoes[T][17]), float(Tornadoes[T][18])]
                            path = createPath(start, end, 10.0)
                            plotWarnAndPath(path, polygon, torTime, warnTime, Warning[0], outdir)
                            return True

                        else:
                            # Here we do a final check to see if the tornado passed through the warning, but did not
                            # start or end in the warning.
                            start = [float(Tornadoes[T][15]), float(Tornadoes[T][16])]
                            end = [float(Tornadoes[T][17]), float(Tornadoes[T][18])]
                            path = createPath(start, end, 10.0)
                            for i in range(0,len(path[0])):
                                location = Point(path[0][i],path[1][i])
                                if (polygon.contains(location) or (location.within(polygon))):
                                    print(" Tornado Found!")
                                    # Plot the warning
                                    start = [float(Tornadoes[T][15]), float(Tornadoes[T][16])]
                                    end = [float(Tornadoes[T][17]), float(Tornadoes[T][18])]
                                    path = createPath(start, end, 10.0)
                                    plotWarnAndPath(path, polygon, torTime, warnTime, Warning[0], outdir)
                                    return True

    # if we got to this point then no tornado was found; return False
    print(" No tornado found...")
    return False

########################################################################################################################






Warnings = dataReadIn(DataDirectory,WARfilename)
Tornadoes = dataReadIn(DataDirectory,LSRfilename)
TorTimes = getTornadoTimesList(Tornadoes)


data = []
for Warning in Warnings:
    try:
        if Warning[1] == "TO":
            print(Warning)

            # #### Categorical Block ####
            date = datetime.datetime.strptime(Warning[2], "%Y%m%d%H%M")
            if date.hour < 12:
                date = date - datetime.timedelta(days=1)
            datestring = datetime.datetime.strftime(date, "%Y%m%d")
            print("\nTrying to find outlook for date " + datestring)
            outlook_shapefile = getShapefile(datestring)
            if outlook_shapefile is None:
                exit()
            else:
                category = getCat(Warning, outlook_shapefile, plot=False, date=datestring)

            #### Verification Block ####
            verified = checkForLSR(Warning, Tornadoes, TorTimes)

            data.append([Warning[0],Warning[2],category,verified])

    except:
        print("\nWarning: Error while reading the line:")
        print(Warning)

# Write output to CSV
with open(DataDirectory+"tor_verification.csv", 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    for line in data:
        print(line)
        csvwriter.writerow(line)
csvfile.close()