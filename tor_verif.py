import os
import csv
import datetime
import numpy as np
from ast import literal_eval
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

DataDirectory = 'H:\\Research\\FalseAlarm\\' # Path to where your metar data is stored
outdir = 'H:\\Research\\FalseAlarm\\' # directory where you want output images to be saved to
WARfilename = 'ConWarnings_2015_2018.csv'
LSRfilename = '2015_2018_tor.csv'


def dataReadIn(DataDirectory,filename):
    print("Processing file: " + DataDirectory + filename+"\n")
    output = []
    os.chdir(DataDirectory)
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
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



def checkForLSR(Warning,Tornadoes,TorTimes):
    beginTime = datetime.datetime.strptime(Warning[2],"%Y%m%d%H%M")
    endTime = datetime.datetime.strptime(Warning[3],"%Y%m%d%H%M")
    TorTimes = np.asarray(TorTimes)
    # This line is returning an array of indices of TorTimes where the beginning time matches the year, month, and day of the tornado event
    PossibleTors = np.where([(Y.year == beginTime.year) and (Y.month == beginTime.month) and (Y.day == beginTime.day) for Y in TorTimes])[0]


    if len(PossibleTors) == 0: # If we couldn't find any possible tornadoes to match the start time then we'll check the end time in case
                                # we switched UTC day.
        PossibleTors = np.where([(Y.year == endTime.year) and (Y.month == endTime.month) and (Y.day == endTime.day) for Y in TorTimes])[0]


    if len(PossibleTors) == 0:
        print("No tornadoes found on this date")
        return False # At this point, there's no need to go further since no tornadoes happened on this day for this warning.


    #print(TorTimes[PossibleTors])
    #print(beginTime, endTime)

    # Check to see if any of the tornadoes occurred during the time frame of the warning
    PossibleTors = np.where([(T <= endTime) and (T >= beginTime) for T in TorTimes[PossibleTors]])[0]

    if len(PossibleTors) == 0:
        print("No tornadoes found during this warning")
        return False # At this point, there's no need to go further since no tornadoes happened during the time span of this warning.


    print("Tornadoes found during this warning")
    # Create the warning Polygon first
    polygon = createPolygon(Warning[4])

    # Now let's check each possible tornado to see if it fell within the polygon
    for T in PossibleTors:
        beginPoint = Point(float(Tornadoes[T][16]), float(Tornadoes[T][15])) # Note that Point takes lon, lat pair
        endPoint = Point(float(Tornadoes[T][18]), float(Tornadoes[T][17]))

        # Check for the begin/end points first
        if (polygon.contains(beginPoint) or (beginPoint.within(polygon))):
            print("Tornado found!")
            return True
        # If that didn't work, then check the end point
        elif (polygon.contains(endPoint) or (endPoint.within(polygon))):
            print("Tornado found!")
            return True
        else:
            print("No Tornado found.")


        # now that we've checked the two obvious points, we'll have to check the in-between area.
        # Note that we're going to assume each tornado follows a straight path from the beginning to end point
        # This is obviously not the case in real life, but the exact paths are difficult to obtain/process.
        beginLat = float(Tornadoes[T][15])
        beginLon = float(Tornadoes[T][16])
        endLat = float(Tornadoes[T][17])
        endLon = float(Tornadoes[T][18])

        print(beginLat,endLat)

        increment = 10 # 1/degrees
        deltaX = (endLon - beginLon) / increment
        deltaY = (endLat - beginLat) / increment
        lats = []
        lat = beginLat
        # Need to figure out this algorithm





Warnings = dataReadIn(DataDirectory,WARfilename)
Tornadoes = dataReadIn(DataDirectory,LSRfilename)
TorTimes = getTornadoTimesList(Tornadoes)



for Warning in Warnings[0:40]:
    if Warning[1] == "TO":
        checkForLSR(Warning,Tornadoes,TorTimes)

