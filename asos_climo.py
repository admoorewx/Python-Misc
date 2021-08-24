import pandas as pd
import numpy as np
import datetime as DT

filename = "H:/Research/Climo/OKC.csv"

# Data Read in
data = pd.read_csv(filename)
valid = data['valid']
temps = data['tmpc']
dewps = data['dwpc']
relh = data['relh']
wspd = data['sknt']
pres = data['mslp']

# Clean the data - set "M" values to np.nan
# Note that "M" denotes missing data as set by the IA mesonet asos data download page
# (https://mesonet.agron.iastate.edu/request/download.phtml)
missing_inds = np.where(temps == "M")[0]
temps[missing_inds] = np.nan

missing_inds = np.where(dewps == "M")[0]
dewps[missing_inds] = np.nan

missing_inds = np.where(relh == "M")[0]
relh[missing_inds] = np.nan

missing_inds = np.where(wspd == "M")[0]
wspd[missing_inds] = np.nan

missing_inds = np.where(pres == "M")[0]
pres[missing_inds] = np.nan


# Get a series of days of the year
# First note all the month/day pairs that don't exist
dates_dne = ['0230','0231','0431','0631','0931','1131']
dates = []
for m in np.arange(1,13,1):
    for d in np.arange(1,32,1):
        if m < 10:
            mo = "0"+str(m)
        else:
            mo = str(m)
        if d < 10:
            da = "0"+str(d)
        else:
            da = str(d)
        if mo+da in dates_dne:
            continue
        else:
            dates.append(mo+da)

# Create a list of month/day pairs for each observation/valid time
# We'll use this to grab data later                         0123456789
# Note that the "valid" observation times are in the format YYYY-MM-DD HH:MM
valid_dates = [d[5:7]+d[8:10] for d in valid]
valid_dates = np.asarray(valid_dates)

# Now process the variables. For now, just temp
data_dict = {}
for date in dates:
    inds = np.where(valid_dates == date)[0]
    data_dict[date] = temps[inds].values

