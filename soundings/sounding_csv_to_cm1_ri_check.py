import os, math
import pandas as pd
import numpy as np
from metpy.units import units
from metpy.calc import wind_components, wind_speed, wind_direction, potential_temperature, relative_humidity_from_dewpoint, mixing_ratio_from_relative_humidity, gradient_richardson_number

csv_directory = "/home/admoore/CM1/soundings/"
save_directory = "/home/admoore/CM1/soundings/"

def adjustWind(u,v,ind,adjustment):
    # Reduce the wind magnitude by the adjustment, but make sure
    # that the wind magnitude is not negative!
    weights = [0.1, 0.25, 0.5, 0.75, 0.8, 0.8, 0.8, 0.75, 0.5, 0.25, 0.1]
    inds = np.arange(-5,6,1)
    for i in range(0,len(inds)):
        wspd = wind_speed(u[ind+inds[i]],v[ind + inds[i]])
        wdir = wind_direction(u[ind+inds[i]],v[ind+inds[i]])
        wspd = wspd - (adjustment*weights[i])
        if wspd < 0.0:
            wspd = 0.000001 * (units.meter / units.second)
        u[ind+inds[i]],v[ind+inds[i]] = wind_components(wspd,wdir)
    return u,v

def movingAverageSmooth(data,window):
    """
    Use a centered moving average to smooth the data. Note that a trailing mean is used for the ends.
    Except for the ends, the mean will use window+1 values from data.
    data - input array
    window - how many values to use to compute the centered mean
    """
    smoothed = []
    for i in range(len(data)):
        if i < window:
            subset = data[:i+window+1]
        elif i > len(data)-window:
            subset = data[i-window:]
        else:
            subset = data[i-window:i+window+1]
        smoothed.append(np.mean(subset))
    return smoothed


def checkRi(height,potT,u,v):
    # Check for Ri values < 0.25, which implies turbulence. 
    # If found, reduce the wind values by the adjustment value. 
    # Return the adjusted wind values.
    Turbulent = True
    attempts = 0
    while Turbulent:
        attempts = attempts + 1
        Ri_values = gradient_richardson_number(height,potT,u,v)
        turb_inds = np.where(Ri_values <= 0.25)[0]
        # for ind in turb_inds:
        #     print(ind, height[ind],potT[ind],u[ind],v[ind],Ri_values[ind])
        if len(turb_inds) > 0:
            potT = [T.magnitude for T in potT]
            potT = movingAverageSmooth(potT,2) * units.kelvin

            u = [U.magnitude for U in u]
            v = [V.magnitude for V in v]

            u = movingAverageSmooth(u,2) * units.meter/units.second
            v = movingAverageSmooth(v, 2) * units.meter / units.second
        else:
            Turbulent = False
        if attempts > 50: # If we've reached the limit in the # of attempts, return None values.
            Turbulent = False
            height = None
    return height,potT,u,v


for filename in os.listdir(csv_directory):
    if filename.endswith('.csv'):
        # Read in the data as a Pandas dataframe
        data = pd.read_csv(os.path.join(csv_directory,filename))
        pres = data['pressure'].values * units.hPa
        hght = data['height'].values * units.meter
        temp = data['temperature'].values * units.degC
        dewp = data['dewpoint'].values * units.degC
        u = data['u_wind'].values * units.knots
        v = data['v_wind'].values * units.knots

        # Convert the winds from knots to m/s
        u = u.to('m/s')
        v = v.to('m/s')

        # Calculate Theta for each level
        theta = potential_temperature(pres,temp)
        theta = [T.magnitude for T in theta] # get the values without the units

        # Check for Turbulence. Continue if turbulence is removed. Skip this sounding if not.
        hght, theta, u, v = checkRi(hght, theta * units.kelvin, u, v)

        if hght is not None:
            print(f'Eliminated turbulence from sounding {filename}')
            # Calculate the mixing ratios for each level
            relh = relative_humidity_from_dewpoint(temp,dewp)
            relh = [R.magnitude for R in relh] # get just the magnitudes without the units
            mixr = mixing_ratio_from_relative_humidity(pres,temp,relh)
            mixr = mixr.to('g/kg')
            mixr = [M.magnitude for M in mixr] # get the values without the units

            # organize the first (surface) line for writing
            sfc_pres = round(pres[0].magnitude,2)
            sfc_tht = round(theta[0],2)
            sfc_mxr = round(mixr[0],2)
            surface = "{0:8.2f}\t{1:8.6f}\t{2:8.6f}".format(sfc_pres,sfc_tht,sfc_mxr)

            # Strip away the units so we can write the values to the file
            hght = [H.magnitude for H in hght]
            u = [U.magnitude for U in u]
            v = [V.magnitude for V in v]
            theta = [T.magnitude for T in theta]

            # organize the subsequent lines for writing
            levels = []
            for i in range(1,len(pres)):
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
        else:
            print(f'Sounding {filename} could not be saved.')
            continue

