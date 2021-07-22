import pandas as pd
import csv
from siphon.simplewebservice.wyoming import WyomingUpperAir
import numpy as np
import datetime


soundings = {
    "FWD": ["0707202100","0710202100"],
    "FFC": ["0710202100", "0613202100","0615202100","0701202100"],
    "TLH": ["0710202100"],
    "TBW": ["0710202100","0621202100"],
    "CHS": ["0611202100"],
    "RNK": ["0611202100"],
    "JAX": ["0613202100","0623202100","0630202100"],
    "BMX": ["0613202100"],
    "ILX": ["0613202100"],
    "CRP": ["0615202100"],
    "JAN": ["0615202100"],
    "SHV": ["0707202100"],




}

station = "FWD"
day = "07"
month = "07"
year = "2021"
hour = "12"
date = datetime.datetime.strptime(day+month+year+hour,"%d%m%Y%H")

def getData(date,station):
    df = WyomingUpperAir.request_data(date,station)
    pressure = df['pressure'].values
    temp = df['temperature'].values
    dewp = df['dewpoint'].values
    u = df['u_wind'].values
    v = df['v_wind'].values
    hght = df['height'].values
    return pressure,temp,dewp,u,v,hght

def toCSV(date,station):
    savename = station + "_" + datetime.datetime.strftime(date, "%m%d%Y%H") + ".csv"
    pres, temp, dewp, u, v, hght = getData(date,station)
    fields = ["pressure", "height", "temperature", "dewpoint", "u_wind", "v_wind"]
    with open(savename,'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        for p in range(0,len(pres)):
            csvwriter.writerow([pres[p],hght[p],temp[p],dewp[p],u[p],v[p]])