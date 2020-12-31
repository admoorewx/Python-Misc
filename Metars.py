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


# start = time.time()
# sites = ["KOKC", "KOUN", "KGFK"]


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
        self.cloudCover = []
        self.ceilings = []
        self.vis    = []
        self.precip = []
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
    def addCloudCover(self,cloudcovers):
        self.cloudCover.append(cloudcovers)
    def addCeilings(self,ceilings):
        self.ceilings.append(ceilings)
    def addPrecip(self,precipitation):
        self.precip.append(precipitation)


##################################################################################




def parseAWCxml(metar,child):
    time = child.findtext('observation_time')
    try:
        data = child.findtext('raw_text')
        obsArray = data.split(" ")
    except:
        obsArray = None
    try:
        temp = float(child.findtext('temp_c'))
    except:
        temp = np.nan
    try:
        dewp = float(child.findtext('dewpoint_c'))
    except:
        dewp = np.nan
    try:
        wdir = float(child.findtext('wind_dir_degrees'))
    except:
        wdir = np.nan
    try:
        wspd = float(child.findtext('wind_speed_kt'))
    except:
        wspd = np.nan
    try:
        gust = float(child.findtext('wind_gust_kt'))
    except:
        gust = np.nan
    try:
        precip = float(child.findtext('pcp1hr_in'))
    except:
        precip = 0.0
    try:
        visby = float(child.findtext('visibility_statute_mi'))
    except:
        visby = np.nan
    try:
        pres = float(child.findtext('altim_in_hg')) / 0.029530
    except:
        pres = np.nan
    try:
        wxstring = child.findtext('wx_string')
    except:
        wxstring = None
    try:
        cloudcovers = []
        ceilings = []
        clouds = child.findall('sky_condition')
        for cloud in clouds:
            cloudcovers.append(cloud.attrib['sky_cover'])
            ceilings.append(cloud.attrib['cloud_base_ft_agl'])
    except:
        cloudcovers = [None]
        ceilings = [None]
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
    metar.addCloudCover(cloudcovers)
    metar.addCeilings(ceilings)
    metar.addPrecip(precip)


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
                metar = METAR(siteID, lat, lon)
                parseAWCxml(metar,child)
                obs_list.append(metar)
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
    # Do a quick check to see if the call has requested only the most recent obs (numHours = 0)
    # if so, set lastOnly to true, but get the last hour's worth of obs
    if numHours == 0:
        numHours = 1
        lastOnly = True
    else:
        lastOnly = False
    url = "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&stationString="+site.upper()+"&hoursBeforeNow="+str(numHours)
    response = requests.get(url)
    tree = ET.fromstring(response.content)
    data = tree[6]
    # Check again to see if we only want the most recent observation
    # if so, then set end to 1 to get the latest ob. Otherwise return all obs.
    if lastOnly:
        end = 1
    else:
        end = len(data)
    # First check to make sure there are valid observations
    try:
        siteID = data[0].findtext('station_id')
        lat = float(data[0].findtext('latitude'))
        lon = float(data[0].findtext('longitude'))
        metar = METAR(siteID, lat, lon)
        for child in reversed(data[:end]): # going in reverse so we add data in chronological order
                # Check to make sure there is a valid observation for this time
                time = child.findtext('observation_time')
                if "M" in time:
                    pass
                else:
                    parseAWCxml(metar,child)
    except:
        pass
    return metar



def multipleMetars(siteList):
    obs_list = []

    for site in siteList:
        if siteList.index(site) == 0:
            siteString = site.upper()
        else:
            siteString = siteString+","+site.upper()

    url = "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=1&stationString=" + siteString
    #works up to here!
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
                if len(obs_list) > 0 and siteID == obs_list[-1].siteID:
                    pass
                else:
                    metar = METAR(siteID, lat, lon)
                    parseAWCxml(metar,child)
                    obs_list.append(metar)
        except:
            pass
    return obs_list

########################################################################################3


#metars = singleMetar("kokc",4)

#print(metars)
#print(metars.times)
#print(metars.dewps)

# obs_list = multipleMetars(sites)
# for ob in obs_list:
#     print(ob)


#
# end = time.time()
# print("")
# print("Elapsed Time:")
# print(end-start)