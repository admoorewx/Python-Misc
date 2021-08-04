from datetime import datetime, timedelta
from metpy.units import units
import pandas as pd
from siphon.simplewebservice.wyoming import WyomingUpperAir
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import metpy.plots as mpplots
from metpy.calc import equivalent_potential_temperature, relative_humidity_from_dewpoint, mixing_ratio_from_relative_humidity
import numpy as np
import os

csv_directory = "H:/Python/Python-Misc/soundings/"
save_directory = "H:/Python/Python-Misc/soundings/"


def getData(csvfile):
    df = pd.read_csv(csvfile)
    pressure = df['pressure'].values * units.hPa
    temp = df['temperature'].values * units.degC
    dewp = df['dewpoint'].values * units.degC
    u = df['u_wind'].values * units.meter/units.second
    v = df['v_wind'].values * units.meter/units.second
    hght = df['height'].values * units.meters
    return pressure,temp,dewp,u,v,hght

def getDiff(pres,thetae):
    # Just get the numbers:
    pres = [p.magnitude for p in pres]
    pres = np.asarray(pres)
    # get the max temp in the lowest X mb:
    top_lower_layer = 700.0 # mb - Top of the bottom layer
    lower_layer_inds = [np.where(pres >= top_lower_layer)][0]
    max_temp = np.nanmax(thetae[lower_layer_inds])

    # get the min temp in the upper portion
    top_upper_layer = 100.0 # mb - where to stop looking for the min temp
    upper_layer_inds = [np.where(pres >= top_upper_layer)][0]
    #upper_layer_inds = [np.where(pres[upper_layer_inds] <= top_lower_layer)][0] # make sure to exclude the lower layer
    min_temp = np.nanmin(thetae[upper_layer_inds])

    diff = max_temp - min_temp
    return diff

def getTheta(pres,temp, dewp):
    # Calculate Theta for each level
    thetae = [equivalent_potential_temperature(pres, temp, dewp)]
    thetae = [T.magnitude for T in thetae]  # get the values without the units
    thetae = thetae[0]  # for some reason the above method returns a 2-D array
    return thetae

def plotThetavPres(filename,filepath):

    sounding_site = filename[0:3]
    sounding_date = filename[4:-4]
    pres, temp, dewp, u, v, hght = getData(filepath)
    thetae = getTheta(pres,temp,dewp)

    # Get the difference in theta-e
    diff = getDiff(pres,thetae)

    fig, ax = plt.subplots()
    ax.plot(thetae,pres,color='firebrick')
    ax.set_ylim(1000.0,100.0)
    ax.set_xlim(250.0,450.0)
    ax.grid(color='gray',linestyle='--')
    ax.text(380.0,200,"Theta-e Deficit: "+str(round(diff,1))+" K",bbox={'facecolor':'0.9','edgecolor':'k','boxstyle':'square'})
    title = "Theta-e Profile at "+sounding_site +" on "+ sounding_date
    plt.title(title)
    plt.ylabel("Pres (hPa)")
    plt.xlabel("Theta-e (K)")

    #plt.show()
    plt.savefig(save_directory+sounding_site+"_"+sounding_date+".png")
    plt.clf()

### Main Function ####
for filename in os.listdir(csv_directory):
    if filename.endswith('.csv'):
        plotThetavPres(filename, os.path.join(csv_directory,filename))