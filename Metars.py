import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import numpy as np
import time

"""
TO DO: 
- Figure out how to parse the cloud and ceiling information
  May be able to do something like this: 
  <bar key="value">text</bar>
  child.find("./bar").attrib['key']
  returns value
"""


start = time.time()
sites = ["KOKC", "KOUN", "KGFK"]


class METAR:
    def __init__(self,siteID,lat,lon):
        self.lat = lat
        self.lon = lon
        self.siteID = siteID
        self.times = []
        self.temps = []
        self.dewps = []
        self.wdirs = []
        self.wspds = []
        self.gusts = []
        self.wx    = []
        self.press = []
        self.clouds = []
        self.ceilings = []
        self.vis    = []
        self.rawObs = []


    def __str__(self):
        return f'Site: {self.siteID}\n' \
            f'Lat: {self.lat}\n' \
            f'Lon: {self.lon}\n' \
            f'Number of observations: {len(self.rawObs)}\n'


    # routines for adding in variables
    def addTemp(self,temp):
        self.temps.append(temp)
    def addDewp(self,dewp):
        self.dewps.append(dewp)
    def addRawObservation(self,obsArray):
        if obsArray is not None:
            self.rawObs.append(obsArray)
    def addTime(self,timestring):
        self.times.append(timestring)
    def addWdir(self,wdir):
        self.wdirs.append(wdir)
    def addWspd(self,wspd):
        self.wspds.append(wspd)
    def addGust(self,gust):
        self.gusts.append(gust)
    def addWx(self,wxstring):
        self.wx.append(wxstring)
    def addPres(self,pres):
        self.press.append(pres)
    def addVis(self,visby):
        self.vis.append(visby)
    def addClouds(self,cloudcover):
        self.clouds.append(cloudcover)
    def addCeilings(self,ceilString):
        self.ceilings.append(ceilString)







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
    for child in data:
        # First check to make sure there is a valid observations
        try:
            siteID = child.findtext('station_id')
            lat = float(child.findtext('latitude'))
            lon = float(child.findtext('longitude'))
            time = child.findtext('observation_time')
            if "M" in time:
                pass
            else:

                try:
                    data = child.findtext('raw_text')
                    obsArray = data.split(" ")
                except:
                    obsArray = None
                try:
                    temp = float(child.findtext('temp_c'))
                except:
                    temp = 9999.0
                try:
                    dewp = float(child.findtext('dewpoint_c'))
                except:
                    dewp = 9999.0
                try:
                    wdir = child.findtext('wind_dir_degrees')
                except:
                    wdir = None
                try:
                    wspd = float(child.findtext('wind_speed_kt'))
                except:
                    wspd = 9999.0
                try:
                    gust = float(child.findtext('wind_gust_kt'))
                except:
                    gust = 9999.0
                try:
                    visby = float(child.findtext('visibility_statute_mi'))
                except:
                    visby = 9999.0
                try:
                    pres = float(child.findtext('sea_level_pressure_mb'))
                except:
                    pres = 9999.0
                try:
                    wxstring = child.findtext('wx_string')
                except:
                    wxstring = None
                # Done getting data, now pass it along to the METAR object
                metar = METAR(siteID,lat,lon)
                metar.addRawObservation(obsArray)
                metar.addTemp(temp)
                metar.addDewp(dewp)
                metar.addWdir(wdir)
                metar.addWx(wxstring)
                metar.addTime(time)
                metar.addPres(pres)
                metar.addVis(visby)
                metar.addWspd(wspd)
                metar.addGust(gust)
                obs_list.append(metar)
                print(metar)
        except:
            pass
    return obs_list




def singleMetar(site,numHours):
    """
    input:
    site: (string) Four letter ID of the ASOS/AWOS location (example: KOKC for Oklahoma City, OK)
    numHours: (int) Number of hours in the past you want to retrive obs.
    return: A single METAR object
    Purpose: This function will use the AWC text dataserver to retrieve all recent METAR
             observations from a single site from (numHours) hours ago.
    """
    obs_list = []
    url = "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&stationString="+site.upper()+"&hoursBeforeNow="+str(numHours)
    print(url)
    response = requests.get(url)
    tree = ET.fromstring(response.content)
    data = tree[6]
    # First check to make sure there are valid observations
    try:
        siteID = data[0].findtext('station_id')
        lat = float(data[0].findtext('latitude'))
        lon = float(data[0].findtext('longitude'))
        metar = METAR(siteID, lat, lon)
        for child in reversed(data): # going in reverse so we add data in chronological order
                # Check to make sure there is a valid observation for this time
                time = child.findtext('observation_time')
                if "M" in time:
                    pass
                else:

                    try:
                        data = child.findtext('raw_text')
                        obsArray = data.split(" ")
                    except:
                        obsArray = None
                    try:
                        temp = float(child.findtext('temp_c'))
                    except:
                        temp = 9999.0
                    try:
                        dewp = float(child.findtext('dewpoint_c'))
                    except:
                        dewp = 9999.0
                    try:
                        wdir = child.findtext('wind_dir_degrees')
                    except:
                        wdir = None
                    try:
                        wspd = float(child.findtext('wind_speed_kt'))
                    except:
                        wspd = 9999.0
                    try:
                        gust = float(child.findtext('wind_gust_kt'))
                    except:
                        gust = 9999.0
                    try:
                        visby = float(child.findtext('visibility_statute_mi'))
                    except:
                        visby = 9999.0
                    try:
                        pres = float(child.findtext('sea_level_pressure_mb'))
                    except:
                        pres = 9999.0
                    try:
                        wxstring = child.findtext('wx_string')
                    except:
                        wxstring = None
                    # Done getting data, now pass it along to the METAR object
                    metar.addRawObservation(obsArray)
                    metar.addTemp(temp)
                    metar.addDewp(dewp)
                    metar.addWdir(wdir)
                    metar.addWx(wxstring)
                    metar.addTime(time)
                    metar.addPres(pres)
                    metar.addVis(visby)
                    metar.addWspd(wspd)
                    metar.addGust(gust)
    except:
        pass
    return metar




metars = singleMetar("kokc",4)

print(metars.times)
print(metars.temps)
print(metars.dewps)

#obs_list = bulkMetars()



end = time.time()
print("")
print("Elapsed Time:")
print(end-start)