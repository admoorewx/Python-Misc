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

    def getTemps(self,type=None):
        if type == None:
            type = "temp"
        temp = []
        dewp = []
        for obs in self.rawObs: # loop through each observation
            for item in obs: # loop through each data item in the observation
                if "/" in item and len(item) <= 7 and (item.index("/") > 1): # the temp/dewpoint will always have a "/" and be less than 8 char long
                    slashLoc = item.index("/")
                    t = item[0:slashLoc]
                    d = item[slashLoc+1:]
                    t = self.toFloat(t)
                    d = self.toFloat(d)
                    temp.append(t)
                    dewp.append(d)
        if type == "dewp":
            return dewp
        else:
            return temp

    def getDewps(self,Obstype="dewp"):
        return self.getTemps(Obstype)


def bulkMetars():
    url = 'https://www.aviationweather.gov/adds/dataserver_current/current/metars.cache.xml'
    response = requests.get(url)
    tree = ET.fromstring(response.content)
    data = tree[6]
    for child in data:

        # Filter data by some metric (i.e. temp)
        # try:
        #     if float(child.findtext('temp_c')) <= 0.0:
        #         print("Site:         " + child.findtext('station_id'))
        #         print("Raw METAR:    " + child.findtext('raw_text'))
        #         print("Temp (C):     " + child.findtext('temp_c'))
        #         print("Dewpoint (C): " + child.findtext('dewpoint_c'))
        #         print("")
        # except:
        #     continue

        # Filter data by site list
        try:
            if child[1].text in sites:
                print("Site:         "+child.findtext('station_id'))
                print("Raw METAR:    "+child.findtext('raw_text'))
                print("Temp (C):     "+child.findtext('temp_c'))
                print("Dewpoint (C): "+child.findtext('dewpoint_c'))
                print("")
        except:
            continue

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

metar = singleMetar("KGFK",24)
metar.getTemps()
dewp = metar.getDewps()
print(dewp)


end = time.time()
print("")
print("Elapsed Time:")
print(end-start)