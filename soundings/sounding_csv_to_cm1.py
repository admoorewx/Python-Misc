import os
import pandas as pd
import numpy as np
from metpy.units import units
from metpy.calc import potential_temperature, relative_humidity_from_dewpoint, mixing_ratio_from_relative_humidity

csv_directory = "/home/icebear/CM1/soundings/"
save_directory = "/home/icebear/CM1/soundings/"


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
        theta = [potential_temperature(pres,temp)]
        theta = [T.magnitude for T in theta] # get the values without the units
        theta = theta[0] # for some reason the above method returns a 2-D array

        # Calculate the mixing ratios for each level
        relh = [relative_humidity_from_dewpoint(temp,dewp)]
        relh = [R.magnitude for R in relh] # get just the magnitudes without the units
        mixr = mixing_ratio_from_relative_humidity(pres,temp,relh)
        mixr = mixr.to('g/kg')
        mixr = [M.magnitude for M in mixr] # get the values without the units
        mixr = mixr[0] # for some reason the above method returns a 2-D array

        # organize the first (surface) line for writing
        sfc_pres = round(pres[0].magnitude,2)
        sfc_tht = round(theta[0],2)
        sfc_mxr = round(mixr[0],2)
        surface = "{0:8.2f}\t{1:8.6f}\t{2:8.6f}".format(sfc_pres,sfc_tht,sfc_mxr)

        # Strip away the units so we can write the values to the file
        hght = [H.magnitude for H in hght]
        u = [U.magnitude for U in u]
        v = [V.magnitude for V in v]

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

