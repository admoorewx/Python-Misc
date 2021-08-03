import pandas as pd
import csv, os
from siphon.simplewebservice.wyoming import WyomingUpperAir
import numpy as np
import datetime

"""
This script retrives observed soundings from the Wyoming sounding arvhive (http://weather.uwyo.edu/upperair/sounding.html)
and saves the data to a csv file. Data formats and units are as follows: 

Pressure (hPa)  Height (m)  Temperature (deg C)     Dewpoint (deg C)    U wind (knots)  V wind (knots)

"""

savedirectory = "/home/icebear/CM1/soundings/"

soundings = {
    "LZK" : ["0722202112"],
    # "FWD": ["0707202100","0710202100"],
    # "FFC": ["0710202100", "0613202100","0615202100","0701202100"],
    # "TLH": ["0710202100"],
    # "TBW": ["0710202100","0621202100"],
    # "CHS": ["0611202100"],
    # "RNK": ["0611202100"],
    # "JAX": ["0613202100","0623202100","0630202100"],
    # "BMX": ["0613202100"],
    # "ILX": ["0613202100"],
    # "CRP": ["0615202100"],
    # "JAN": ["0615202100"],
    # "SHV": ["0707202100"],
}


def getData(date,station):
    date = datetime.datetime.strptime(date,"%m%d%Y%H")
    df = WyomingUpperAir.request_data(date,station)
    pressure = df['pressure'].values
    temp = df['temperature'].values
    dewp = df['dewpoint'].values
    u = df['u_wind'].values
    v = df['v_wind'].values
    hght = df['height'].values
    return pressure,temp,dewp,u,v,hght

def toCSV(date,station):
    savename = station + "_" + date + ".csv"
    pres, temp, dewp, u, v, hght = getData(date,station)
    fields = ["pressure", "height", "temperature", "dewpoint", "u_wind", "v_wind"]
    with open(os.path.join(savedirectory,savename),'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        for p in range(0,len(pres)):
            csvwriter.writerow([pres[p],hght[p],temp[p],dewp[p],u[p],v[p]])

### Main function ###
for stid,dates in soundings.items():
    for date in dates:
        toCSV(date,stid)
