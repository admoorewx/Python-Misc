import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import numpy as np
import time

start = time.time()
sites = ["KOKC", "KOUN", "KGFK"]
testLat = 32.0
testLon = -96.0

class METAR:
    def __init__(self,siteID,lat,lon,obsArray):
        self.lat = lat
        self.lon = lon
        self.siteID = siteID
        self.rawObs = []
        if obsArray is not None:
            self.rawObs.append(obsArray)

    def __str__(self):
        return f'Site: {self.siteID}\n' \
            f'Lat: {self.lat}\n' \
            f'Lon: {self.lon}\n' \
            f'Number of observations: {len(self.rawObs)}\n'

    def addObservation(self,obsArray):
        if obsArray is not None:
            self.rawObs.append(obsArray)

    def toFloat(self,t):
        # Takes in a temperature string (such as "M04") and converts it to a float number (such as -4.0)
        try:
            t = float(t)
        except:
            t = 0.0 - float(t[1:])
        return t

    def getTemps(self):
        temp = []
        for obs in self.rawObs: # loop through each observation
            for item in obs: # loop through each data item in the observation
                # This filter checks for:
                # 1) looks for the "/" present in all T/Td obs
                # 2) Makes sure the char length is less than 8 (always will be unless the world has ended)
                # 3) Ensures the "/" is roughly in the correct spot (filters out some RMK codes)
                # 4) Ensures that any observation with SM (i.e. M1/4SM) is not included
                # 5) Ensures that the "/" only occurs once - excludes some RMK codes
                if "/" in item \
                        and len(item) >= 3 \
                        and len(item) <= 7 \
                        and (item.index("/") > 1) \
                        and (item.index("/") < 4) \
                        and "SM" not in item \
                        and item.count("/") == 1:
                    try:
                        slashLoc = item.index("/")
                        t = item[0:slashLoc]
                        t = self.toFloat(t)
                        temp.append(t)
                    except:
                        print(item)
                        # Likely a random RMK code at this point, just ignore
                        pass
        return temp

    def getDewps(self):
        dewp = []
        for obs in self.rawObs: # loop through each observation
            for item in obs: # loop through each data item in the observation
                # This filter checks for:
                # 1) looks for the "/" present in all T/Td obs
                # 2) Makes sure the char length is less than 8 (always will be unless the world has ended)
                # 3) Ensures the "/" is roughly in the correct spot (filters out some RMK codes)
                # 4) Ensures that any observation with SM (i.e. M1/4SM) is not included
                # 5) Ensures that the "/" only occurs once - excludes some RMK codes
                if "/" in item and \
                        len(item) <= 7 \
                        and len(item) >= 5 \
                        and (item.index("/") > 1) \
                        and (item.index("/") < 4) \
                        and "SM" not in item \
                        and item.count("/") == 1:
                    try:
                        slashLoc = item.index("/")
                        d = item[slashLoc+1:]
                        d = self.toFloat(d)
                        dewp.append(d)
                    except:
                        print(item)
                        # Likely a random RMK code at this point, just ignore
                        pass
        return dewp

    def getWind(self):
        wspds = []
        wdirs = []
        gusts = []
        for obs in self.rawObs:
            try:
                if "KT" not in obs[2]: # Make sure this isn't an "auto" or "cor"
                    raw_wind = obs[3]
                else:
                    raw_wind = obs[2]
                wdir = raw_wind[0:3]
                wspd = raw_wind[3:5]
                if len(raw_wind) > 7:
                    gust = raw_wind[6:8]
                else:
                    gust = "00"
                if "E" not in wdir and "/" not in wdir:
                    wdirs.append(wdir)
                    wspds.append(float(wspd))
                    gusts.append(float(gust))
            except:
                pass
        if len(self.rawObs) == 1:
            return wdir, wspd, gust
        else:
            return wdirs, wspds, gusts



def bulkMetars():
    """
    This function will use the AWC text dataserver to retrieve all recent METAR
    observations and create a list of METAR objects. Each observation becomes its
    own METAR object.
    :return: A list of METAR objects
    """
    obs_list = []
    url = 'https://www.aviationweather.gov/adds/dataserver_current/current/metars.cache.xml'
    response = requests.get(url)
    tree = ET.fromstring(response.content)
    data = tree[6]
    #counter = 0 # uncomment to track # of bad obs
    for child in data:
        try:
            data = child.findtext('raw_text')
            siteID = child.findtext('station_id')
            lat = float(child.findtext('latitude'))
            lon = float(child.findtext('longitude'))
            obsArray = data.split(" ")
            if obsArray[1] == "M": # This is a filter for bad data with no valid time
                #counter = counter + 1 # uncomment to track # of bad obs
                continue
            else:
                metar = METAR(siteID,lat,lon,obsArray)
                obs_list.append(metar)
        except:
            pass
            # Must have encountered data with no lat/lon info! Ignore these. Uncomment for debugging info
            # siteID = child.findtext('station_id')
            # print("\nProblem finding data at site: "+siteID)
            # print("Debug Info:")
            # print("lat:")
            # print(child.findtext('latitude'))
            # print("lon:")
            # print(child.findtext('longitude'))
            # print("raw text:")
            # print(child.findtext('raw_text'))
            #counter = counter + 1 # uncomment to track # of bad obs

    #print("Bad Obs Encountered: "+str(counter)) # uncomment to output number of bad obs
    return obs_list


def singleMetar(site,numHours):
    """
    :param site: 4-letter identifier for the METAR location the user is requesting (example: KOUN for Norman, OK)
                 This needs to be in all CAPS!
    :param numHours: The number of hours that you want to retrieve. Example: 24 will return the past 24 hours worth of observations
                     Note: available options are 1, 12, 24, and 48 hours (per AWC)
    :return: will return a METAR object that contains the observations.

    to-do: need to read-in the lat/lon of a site from the stations list
           need to see how to pass in a METAR object and just add observations
    """
    url = 'https://www.aviationweather.gov/metar/data?ids='+site+'&format=raw&date=&hours='+str(numHours)
    response = requests.get(url)
    data = BeautifulSoup(response.text, features="html.parser")
    code = data.find_all('code')
    metar = METAR(site, testLat, testLon, None)
    for item in code:
        #metarParser(item)
        obsArray = item.contents[0].split(' ')
        metar.addObservation(obsArray)
    return metar

obs_list = bulkMetars()
for ob in obs_list:
    temps = ob.getWind()
    print(temps)


end = time.time()
print("")
print("Elapsed Time:")
print(end-start)