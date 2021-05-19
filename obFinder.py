"""
This script is designed to take in the lat/lon of a severe wind report and then find the nearest measured wind speed or gust.
This is done by iteratively increasing a radius in which to check for possible ASOS/AWOS sites (or perhaps mesonet sites if applicable).
"""

import os,csv
import numpy as np
import requests
import datetime
from math import radians, cos, sin, asin, sqrt
import matplotlib.pyplot as plt

DataDirectory = 'H:\\Research\\WindDamage\\stormdata\\' # Path to where your metar data is stored
outdir = 'H:\\Research\\WindDamage\\' # directory where you want output images to be saved to
#filename  = 'stormevents_details_2020.csv'
FAAlist = 'stations.csv'


def parseData(row):
    try:
        datestring = row[0][0:4] + "-" + row[0][4:] + "-" + row[1] + " " + row[2]
        date = datetime.datetime.strptime(datestring, "%Y-%m-%d %H%M")
        if "EST" in row[18]:
            dt = 5
        elif "CST" in row[18]:
            dt = 6
        elif "MST" in row[18]:
            dt = 7
        elif "PST" in row[18]:
            dt = 8
        else:
            dt = 0
        timezone_offset = datetime.timedelta(hours=dt)
        date = date + timezone_offset  # convert to UTC time
        lat = float(row[44])
        lon = float(row[45])
        description = row[49]
        gust = float(row[27])
        return [date, lat, lon, gust, description]
    except:
        print("Warning, had problem parsing data in row:")
        print(row)
        return None

def stormDataReadIn(DataDirectory,filename,state=None):
    # Read in a "stormEvents_details" CSV file from Storm Data (ftp.ncdc.noaa.gov/pub/data/swdi/stormevents/csvfiles/)
    # return The time, lat, lon, estimated wind gust, and damage report as an array.
    # Input a state name in all caps if you want wind reports from just that state. Example: "state = OKLAHOMA"
    print("Processing file: " + DataDirectory + filename+"\n")
    output = []
    os.chdir(DataDirectory)
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        eventID = 1
        for row in csv_reader:
            if "Thunderstorm Wind" in row[12]: # Make sure we're looking at only thunderstorm wind gusts
                if state is not None:
                    if row[8] == state and row[28] == "EG": # Satisfy the state filter and estimated gust filter
                        parsed = parseData(row)
                        if parsed is not None:
                            output.append(parseData(row))
                        else:
                            continue

                elif row[28] == "EG": # If we don't have a state filter, check for estimated gust
                    parsed = parseData(row)
                    if parsed is not None:
                        output.append(parseData(row))
                    else:
                        continue
    csv_file.close()
    return output


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r


def readFAAStationList(DataDirectory,filename):
    # Read in a CSV file of ASOS/AWOS station information and
    # return an array of [siteID,lat,lon] for all sites.
    print("Processing file: " + DataDirectory + filename+"\n")
    output = []
    os.chdir(DataDirectory)
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            output.append([row[1],float(row[3]),float(row[4])])
    csv_file.close()
    return output

def findNearestOb(time,lat,lon,radius,timewindow,stationList):
    """
    :param time: datetime object of when the event occurred
    :param lat: latitude at which the event occurred
    :param lon: longitude at which the event occurred
    :param radius: (km) Radius around the lat/lon of the event that you want to search
    :param timewindow: (minutes) Allowable time error between event and measured wind.
    :param stationList: list of stations that you want to check. Needs to have format [[siteID,lat,lon],...]
    :return: an array that contains the result information:

                    [measured wind, measured time, station lat, station lon, station ID, distance from event, time difference]

            Note: if more than one observation is found within the search radius then the closest observation is returned (for now).
            Note: If no stations are found, or no data is found within the time window, then an empty array is returned.
    """
    # first find some stations that fall within our search radius.
    contenders = []
    for site in stationList:
        #print(lon,lat,site[2],site[1])
        distance = haversine(lon,lat,site[2],site[1])
        #print(distance)
        if distance < radius:
            contenders.append([site[0],distance,site[1],site[2]])


    if len(contenders) > 0: # if we found stations within the radius, then find data from the closest station

        # now try to get data from the IA state mesonet for each of the possible contenders
        year1 = time.year
        month1 = time.month
        day1 = time.day
        # Get the datetime object for 24 hours into the future (so we can get 24-hours worth of data).
        time2 = time + datetime.timedelta(days=1)
        year2 = time2.year
        month2 = time2.month
        day2 = time2.day

        # Get data from the closest station within the requested radius
        # Note that the wind speed data is all in knots.
        mins = [contenders[x][1] for x in range(0,len(contenders))]
        min_dist = np.min(mins)
        loc = mins.index(min_dist)
        id = contenders[loc][0][1:].upper()
        url = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station="+id+"&data=sknt&data=gust&data=peak_wind_gust&data=peak_wind_time&year1="+str(year1)+"&month1="+str(month1)+"&day1="+str(day1)+"&year2="+str(year2)+"&month2="+str(month2)+"&day2="+str(day2)+"&tz=Etc%2FUTC&format=onlycomma&latlon=no&elev=no&missing=M&trace=T&direct=no&report_type=1&report_type=2"
        response = requests.get(url)

        # Process the HTML response that contains the data
        observations = response.text.split('\n')
        max_wind = np.nan # go ahead and set the max wind as a check for whether or not we found a good ob
        min_time = timewindow # go ahead and set the min_time difference as the requested time window.
        for line in observations[1:-1]: # skips the header line
            line = line.split(",")
            ob_time = datetime.datetime.strptime(line[1], "%Y-%m-%d %H:%M")
            deltaT = ob_time - time
            deltaT = deltaT.total_seconds() / 60.0 # get deltaT in minutes
            if abs(deltaT) <= min_time:
                try:
                    wspd = float(line[2])
                except:
                    wspd = np.nan
                try:
                    gust = float(line[3])
                except:
                    gust = np.nan
                try:
                    pkwnd = float(line[4])
                except:
                    pkwnd = np.nan
                try:
                    pkgust = float(line[5])
                except:
                    pkgust = np.nan
                min_time = abs(deltaT)
                max_ob_time = ob_time
                max_wind = np.nanmax([wspd,gust,pkwnd,pkgust])

        if np.isnan(max_wind): # in case you did not find any obs within the requested time window
            return []
        else: # if you did find an ob within the requested time window
            return [max_wind, max_ob_time, contenders[loc][2], contenders[loc][3], contenders[loc][0], min_dist, min_time]
    else: # in case you did not find any obs in the requested radius
        return []




radius = 25.0 # km
window = 15.0 # minutes
stationList = readFAAStationList(outdir,FAAlist)
NYfound_count = 0
NYnotfound_count = 0
NYestimates = []
NYmeasured = []
NYdistances = []

OKfound_count = 0
OKnotfound_count = 0
OKestimates = []
OKmeasured = []
OKdistances = []

# loop through each CSV file in the data directory
for filename in os.listdir(DataDirectory):
    if filename.endswith(".csv"):
        # Process for NY
        output = stormDataReadIn(DataDirectory, filename, state="NEW YORK")
        for entry in output[0:]:
            matching_wind = findNearestOb(entry[0],entry[1],entry[2],radius,window,stationList)
            if len(matching_wind) > 0:
                NYfound_count = NYfound_count + 1
                NYmeasured.append(matching_wind[0])
                NYestimates.append(entry[3])
                NYdistances.append(matching_wind[5])

            else:
                #print("No observation found")
                NYnotfound_count = NYnotfound_count + 1

        # Process for OK
        output = stormDataReadIn(DataDirectory, filename, state="OKLAHOMA")
        for entry in output[0:]:
            matching_wind = findNearestOb(entry[0],entry[1],entry[2],radius,window,stationList)
            if len(matching_wind) > 0:
                OKfound_count = OKfound_count + 1
                OKmeasured.append(matching_wind[0])
                OKestimates.append(entry[3])
                OKdistances.append(matching_wind[5])

            else:
                #print("No observation found")
                OKnotfound_count = OKnotfound_count + 1




# print("\n\n")
# print(f"Found {found_count} corresponding observations.")
# print(f"Did not find observations for {notfound_count} observations.")

print("OK avg dist: "+str(np.mean(OKdistances)))
print("NY avg dist: "+str(np.mean(NYdistances)))

plt.figure(1)
plt.scatter(NYestimates,NYmeasured,marker='x',color='b',label="NY Count = "+str(NYfound_count))
plt.scatter(OKestimates,OKmeasured,marker='x',color='r',label="OK Count = "+str(OKfound_count))
plt.grid()
plt.legend()
plt.xlabel("Estimated Wind Speed (knots)")
plt.ylabel("Nearest Measured Wind Speed (knots)")
plt.title(f"Wind Damage Wind Est. vs. Nearest Measured Wind Speed \n (Using a {radius} km radius over the period 2017-2020)")
plt.show()