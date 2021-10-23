import os, math
import pandas as pd
import numpy as np
from metpy.units import units
from metpy.calc import potential_temperature, relative_humidity_from_dewpoint, mixing_ratio_from_relative_humidity, gradient_richardson_number
from scipy.interpolate import UnivariateSpline
from sounding_plot_routine import plotSounding

# Schooner
csv_directory = "/home/admoore/CM1/soundings/"
save_directory = "/home/admoore/CM1/soundings/"

# PC
# csv_directory = "H:/Python/Python-Misc/soundings/"
# save_directory = "H:/Python/Python-Misc/soundings/"


def checkHeights(h,p,t,d):
# Make sure that all the heights are increasing
# remove the height (and all data at that height) 
# if the height decreases - consider it invalid.
    inds = []
    for i in range(1,len(h)):
        if h[i] < h[i-1]:
            inds.append(i)
    h = np.delete(h,inds)
    p = np.delete(p,inds)
    t = np.delete(t,inds)
    d = np.delete(d,inds)
    return h, p, t, d

def fixSuperAdiabatic(t,h):
    """
    Assume a dry-adiabatic lapse rate of 9.8 C / km
    to change the temperatures of the lowest 2 height levels.
    This will remove any super-adiabatic layers at the surface.
    """
    if len(t) != 3 or len(h) != 3:
        print("ERROR: fixSuperAdiabatic needs the lowest 3 height/temperature levels only.")
    for i in [2,1]:
        t[i-1] = t[i] - ((9.8/1000.0) * (h[i] - h[i-1]))
    print(h)
    print(t)
    return t




for filename in os.listdir(csv_directory):
    if filename.endswith('.csv'):
        # Read in the data as a Pandas dataframe
        data = pd.read_csv(os.path.join(csv_directory,filename))
        pres = data['pressure'].values 
        hght = data['height'].values 
        temp = data['temperature'].values 
        dewp = data['dewpoint'].values 

        for i in range(0,len(pres)):
            print(f'{i} | {hght[i]} | {pres[i]} | {temp[i]} | {dewp[i]}')

        # Clean/QC the data - specifically check the heights
        hght, pres, temp, dewp = checkHeights(hght,pres,temp,dewp)

        # Assign the rest of the units for metpy calcs
        pres = pres * units.hPa
        hght = hght * units.meter
        temp = temp * units.degC
        dewp = dewp * units.degC

        # Calculate Theta for each level
        theta = potential_temperature(pres,temp)
        # Create the zero-ed wind profiles 
        u = [0.0 for H in hght] * units.meter/units.second 
        v = [0.0 for H in hght] * units.meter/units.second

        # Check for Richardson numbers <= 0.25. If found, there is turbulence, do not continue.
        Ri_values = gradient_richardson_number(hght,theta, u, v)
        inds = np.where(Ri_values <= 0.25)[0]

        if len(inds) > 0:
            print("WARNING: Turbulence found in station "+filename[0:3]+"! Attempting to fix.")
            print(inds)
            if 0 in inds:
                # Get only the values, no units
                temp = [T.magnitude for T in temp]
                hght = [H.magnitude for H in hght]
                # try to fix super adiabatic layer
                temp[0:3] = fixSuperAdiabatic(temp[0:3],hght[0:3])
                # re-assign units
                temp = temp * units.degC
                hght = hght * units.meter
                # re-check the Ri values
                Ri_values = gradient_richardson_number(hght, theta, u, v)
                inds = np.where(Ri_values <= 0.25)[0]
                print(inds)


        else:
            print("No turbulence found for sounding "+filename[0:3])
            # Calculate the mixing ratios for each level
            relh = [relative_humidity_from_dewpoint(temp,dewp)]
            relh = [R.magnitude for R in relh] # get just the magnitudes without the units
            mixr = mixing_ratio_from_relative_humidity(pres,temp,relh)
            mixr = mixr.to('g/kg')
            mixr = [M.magnitude for M in mixr] # get the values without the units
            mixr = mixr[0] # for some reason the above method returns a 2-D array

            # organize the first (surface) line for writing
            sfc_pres = round(pres[0].magnitude,2)
            sfc_tht = round(theta[0].magnitude,2)
            sfc_mxr = round(mixr[0],2)
            surface = "{0:8.2f}\t{1:8.6f}\t{2:8.6f}".format(sfc_pres,sfc_tht,sfc_mxr)
            # Strip away the units so we can write the values to the file
            theta = [T.magnitude for T in theta]
            u = [U.magnitude for U in u]
            v = [V.magnitude for V in v]
            hght = [H.magnitude for H in hght]
            # organize the subsequent lines for writing
            levels = []
            for i in range(1,len(hght)):
                level = [hght[i], theta[i], mixr[i], u[i], v[i]]
                if np.isnan(level).any(): # make sure no lines with nans get through
                    continue
                else:
                    # convert to string
                    level = "{0:8.2f}\t{1:8.6f}\t{2:8.6f}\t{3:8.6f}\t{4:8.6f}".format(hght[i], theta[i], mixr[i], u[i], v[i])
                    levels.append(level)
            # print(surface)
            # for L in levels:
            #     print(L)
            ## Write the data to a file ##
            savename = "input_sounding_"+filename[:-4]
            with open(os.path.join(save_directory,savename),"w") as cm1_file:
                cm1_file.write(surface) 
                for L in levels:
                    cm1_file.write("\n")
                    cm1_file.write(L)
            cm1_file.close()

            # plot the sounding
            # pres = np.asarray(pres)*units.hPa
            # hght = np.asarray(hght)*units.meter
            # temp = np.asarray(temp)*units.degC
            # dewp = np.asarray(dewp)*units.degC
            # u = np.asarray(u)*units.meter/units.second
            # v = np.asarray(v) *units.meter/units.second
            # plotSounding(pres,temp,dewp,u,v,hght, station=filename[0:3],date=filename[4:-4])
