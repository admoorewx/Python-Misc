import pandas as pd
import numpy as np
import datetime as DT
import plotly.graph_objects as go
import plotly.subplots as sp
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


def plotlyPlot(dates,stats,site,variable,units):
    dates = [d[0:2]+"/"+d[2:] for d in dates] # format dates for x-axis
    showleg = False # show the line in the legend
    fig = sp.make_subplots(rows=1,cols=1,specs=[
        [{"secondary_y": False}],
    ])

    # plot min line
    fig.append_trace(go.Scatter(x=dates,y=stats[0],name="Minimum Value",
                                 line=dict(color='blue'),showlegend=showleg),row=1,col=1)
        # plot max line
    fig.append_trace(go.Scatter(x=dates,y=stats[6],name="Maximum Value",
                                 line=dict(color='red'),showlegend=showleg),row=1,col=1)
    # plot the mean line
    fig.append_trace(go.Scatter(x=dates,y=stats[3],name="Mean",
                                 line=dict(color='black'),showlegend=showleg),row=1,col=1)
    # plot the 10% line
    fig.append_trace(go.Scatter(x=dates,y=stats[1],name="10th Percentile",
                                 line=dict(color='gray'),showlegend=showleg),row=1,col=1)
    # plot the 90% line
    fig.append_trace(go.Scatter(x=dates,y=stats[5],name="90th Percentile",
                                line=dict(color='gray'),fill='tonexty',showlegend=showleg),row=1,col=1)
    # plot the 25% line
    fig.append_trace(go.Scatter(x=dates,y=stats[2],name="25th Percentile",
                                 line=dict(color='green'),fill=None,showlegend=showleg),row=1,col=1)
    # plot the 75% line
    fig.append_trace(go.Scatter(x=dates,y=stats[4],name="75th Percentile",
                                 line=dict(color='green'),fill='tonexty',showlegend=showleg),row=1,col=1)

    fig.update_yaxes(title=units,row=1,col=1)
    fig.update_xaxes(title="Day/Month",row=1,col=1)
    fig.update_layout(title={'text': f"{variable} Distribution for {site.upper()}",
                      'y': 0.95,
                      'x': 0.5,
                      'xanchor': 'center',
                      'yanchor': 'top'},
                      autosize=True)
    fig.show()


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
stats = getStats(dates,temps)

# plot the data
#plotStats(dates,stats,"OKC","Relative Humidity","Relh (%)")
plotlyPlot(dates,stats,"OKC","Temperature","T (C)")

