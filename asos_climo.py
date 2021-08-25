import pandas as pd
import numpy as np
import datetime as DT
import matplotlib.pyplot as plt

filename = "~/Research/Climo/OKC.csv"


def data_read_in(filename):
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

    return [valid,temps,dewps,wspd,relh,pres]


def getDates():
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
    return dates


def getStats(dates,variable):
    data_dict = {}
    # Now process the variables. 
    for date in dates:
        inds = np.where(valid_dates == date)[0]
        data_dict[date] = variable[inds].values

    # Get some statistics from the dictionary
    means = []
    mins = []
    maxs = []
    p25 = []
    p75 = []
    p10 = []
    p90 = []

    for values in data_dict.values():
        vals = [float(v) for v in values]
        means.append(np.nanmean(vals))
        mins.append(np.nanmin(vals))
        maxs.append(np.nanmax(vals))
        p10.append(np.nanpercentile(vals,10))
        p25.append(np.nanpercentile(vals,25))
        p75.append(np.nanpercentile(vals,75))
        p90.append(np.nanpercentile(vals,90))

    return [mins,p10,p25,means,p75,p90,maxs]


def plotStats(dates,stats,site,variable,units):
    # plot the data from the dictionary
    xvals = np.arange(0,len(dates),1)
    plt.figure(1)
    ax = plt.gca()
    ax.plot(xvals,stats[3],color='k',label="Mean")
    ax.plot(xvals,stats[0],color='b',label="Min")
    ax.plot(xvals,stats[6],color='r',label="Max")
    ax.fill_between(xvals,stats[5],stats[1],color='gray',alpha=0.35)
    ax.fill_between(xvals,stats[4],stats[2],color='g',alpha=0.35)
    ax.set_xticks(xvals[::30])
    ax.set_xticklabels(dates[::30])
    ax.set_xlim(0,xvals[-1])
    ax.set_xlabel("Date")
    ax.set_ylabel(units)
    ax.set_title(site+" "+variable+" Distribution 1950-2020")
    plt.legend()
    plt.show()



# Read in the data
valid, temps, dewps, wspd, relh, pres  = data_read_in(filename)
# Create a list of month/day pairs for each observation/valid time
# We'll use this to grab data later                         0123456789
# Note that the "valid" observation times are in the format YYYY-MM-DD HH:MM
valid_dates = [d[5:7]+d[8:10] for d in valid]
valid_dates = np.asarray(valid_dates)

# create list of dates
dates = getDates()

# Get the stats
stats = getStats(dates,relh)
wind_stats = getStats(dates,wspd)

# plot the data
plotStats(dates,stats,"OKC","Relative Humidity","Relh (%)")
plotStats(dates,wind_stats,"OKC","Sustained Wind Speed","Knots")




