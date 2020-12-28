import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import numpy as np
import time

start = time.time()
sites = ["KOKC", "KOUN", "KGFK"]

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

def singleMetar():
    url = 'https://www.aviationweather.gov/metar/data?ids=KOKC&format=raw&date=&hours=0'
    response = requests.get(url)
    data = BeautifulSoup(response.text, features="html.parser")
    code = data.find_all('code')
    print(code)

singleMetar()

end = time.time()
print("")
print("Elapsed Time:")
print(end-start)