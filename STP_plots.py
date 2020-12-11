import csv
import numpy as np
import matplotlib.pyplot as plt
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from collections import OrderedDict



DataDirectory = 'H:\\Research\\STP\\' # Path to where your metar data is stored
outdir = 'H:\\Research\\' # directory where you want output images to be saved to
filename = 'STP_soundings.csv'
#######################################################################################################################
def dataReadIn(DataDirectory,filename):
    #print("Reading in Data...")
    print("Processing file: " + DataDirectory + '\\' + filename+"\n")
    #print("\nStarting.")
    #print(datetime.datetime.now())
    # Create arrays to hold data
    date = []
    site = []
    lat  = []
    lon  = []
    stpe = []
    stpf = []

    # After a bit of testing, this was found to be the best way to read in the data.
    # Takes about 10 seconds per file, so improvements could be made.
    with open(DataDirectory + filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row[10] is not '':
                continue
            else:
                date.append(row[0])
                site.append(row[1])
                lat.append(float(row[2]))
                lon.append(float(row[3]))
                stpe.append(float(row[4]))
                stpf.append(float(row[5]))

    print("Complete!")
    #print(datetime.datetime.now())
    #print("")
    return date, site, lat, lon, stpe, stpf


def plotSTPDist(stpe,stpf):

    bins = np.arange(0,15,0.25)
    hist,bin_edge = np.histogram(stpe,bins,(0.0,15.0))
    ymax = np.max(hist) + 10
    yloc = ymax - 10

    plt.figure(1)
    plt.subplot(1,2,1)
    plt.hist(stpe, bins=bins, density=False, align='left', rwidth=0.75, color='steelblue')
    plt.title("Effective Layer STP Distribution",fontsize=10)
    plt.xlabel("STP Value")
    plt.ylabel("Frequency")
    plt.xlim(-0.5, 14)
    plt.xticks(np.arange(0,14,1))
    plt.ylim(0,ymax)
    #plt.text(7.0,yloc,"n = "+str(len(stpe)))
    plt.grid(color='gray',alpha=0.65)

    plt.subplot(1,2,2)
    plt.hist(stpf, bins=bins, density=False, align='left', rwidth=0.75, color='steelblue')
    plt.title("Fixed Layer STP Distribution",fontsize=10)
    plt.xlabel("STP Value")
    plt.xlim(-0.5, 14)
    plt.xticks(np.arange(0, 14, 1))
    plt.ylim(0,ymax)
    #plt.text(7.0,yloc,"n = "+str(len(stpf)))
    plt.grid(color='gray',alpha=0.65)

    plt.show()
    #plt.savefig(outdir + "\\Blizzard_SnowAccumHist.png")


    plt.figure(2)
    plt.boxplot([stpe,stpf], labels=["Effective Layer", "Fixed Layer"])
    plt.title("STP Distribution \n n = "+str(len(stpe)),fontsize=10)
    plt.ylabel("STP Value")


    plt.show()


def sortSites(sites,lat,lon):

    site_list = {}
    for s,S in enumerate(sites):
        if S in site_list.keys():
            site_list[S][2] = site_list[S][2] + 1
        else:
            site_list[S] = [lat[s],lon[s], 1]
    return site_list


def plotSoundingMap(site_list):
    ax = plt.axes(projection=ccrs.PlateCarree())
    #ax.add_feature(cartopy.feature.LAND)
    #ax.add_feature(cartopy.feature.OCEAN)
    #ax.add_feature(cartopy.feature.STATES, edgecolor='gray')
    #ax.add_feature(cartopy.feature.COASTLINE)

    # add lakes and international borders
    ax.add_feature(cartopy.feature.LAKES)
    ax.add_feature(cartopy.feature.BORDERS, edgecolor='gray')

    # Add hi-res states
    scale = '110m'
    states50 = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_1_states_provinces_lines',
        scale=scale,
        facecolor='none',
        edgecolor='gray')
    ax.add_feature(states50, zorder=2, linewidth=1)

    # add hi-res coastline (for islands)
    ax.coastlines(resolution='50m', color='gray', linewidth=1)
    # add hi-res land cover
    land_10m = cartopy.feature.NaturalEarthFeature('physical', 'land', '10m')
    ax.add_feature(land_10m, zorder=0, facecolor='white', edgecolor='gray', linewidth=1)
    # change the extent
    ax.set_extent([-125, -65, 23, 50])


    plt.title("Sampled Sounding Locations and Frequency")
    for site,data in site_list.items():
        lat = data[0]
        lon = data[1]
        val = data[2]
        plt.plot(lon, lat, markersize=3, marker='o', color='k')
        plt.text(lon, lat+0.5, site+": "+str(val),
                 horizontalalignment='center',
                 transform=ccrs.PlateCarree(),
                 fontsize=10,
                 weight='bold')
    plt.show()

def plotTemporalDist(date):
    hours = []
    months = []
    years = []

    for day in date:
        hours.append(int(day[9:]))
        months.append(int(day[0:2]))
        year = "20"+day[6:8]
        years.append(int(year))

    hour_bins = np.arange(0,24,1)
    year_bins = [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
    month_bins = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

    plt.figure(1)
    plt.subplot(1,3,1)
    plt.hist(hours, bins=hour_bins, density=False, align='left', rwidth=0.75, color='steelblue')
    plt.title("Observed Sounding Hour Distribution",fontsize=10)
    plt.xlabel("UTC Hour")
    plt.ylabel("Frequency")
    #plt.xlim(0, 23)
    plt.xticks(hour_bins[::2])
    #plt.ylim(0,50)
    #plt.text(7.0,45,"n = "+str(len(date)))
    plt.grid(color='gray',alpha=0.75)

    plt.subplot(1,3,2)
    plt.hist(months, bins=month_bins, density=False, align='left', rwidth=0.75, color='steelblue')
    plt.title("Observed Sounding Month Distribution",fontsize=10)
    plt.xlabel("Month of Year")
    plt.xticks(month_bins)
    plt.xlim(1, 12)
    #plt.ylim(0,50)
    #plt.text(7.0,45,"n = "+str(len(months)))
    plt.grid(color='gray',alpha=0.75)

    plt.subplot(1,3,3)
    plt.hist(years, bins=year_bins, density=False, align='left', rwidth=0.75, color='steelblue')
    plt.title("Observed Sounding Year Distribution",fontsize=10)
    plt.xlabel("Year")
    plt.xticks(year_bins)
    plt.xlim(2013, 2020)
    #plt.ylim(0,50)
    #plt.text(7.0,45,"n = "+str(len(years)))
    plt.grid(color='gray',alpha=0.75)

    plt.show()


def sortByDate(date, lat, lon):
    files = {}
    for d, date in enumerate(date):
        hour = date[9:]
        month = date[0:2]
        day = date[3:5]
        year = date[6:8]
        date_string = year+month+day+hour

        if date_string in files.keys():
            files[date_string][0].append(lat[d])
            files[date_string][1].append(lon[d])
        else:
            files[date_string] = [[lat[d]],[lon[d]]]
    return files

date, site, lat, lon, stpe, stpf = dataReadIn(DataDirectory,filename)

#files = sortByDate(date, lat, lon)
#plotTemporalDist(date)
plotSTPDist(stpe,stpf)
#site_list = sortSites(site,lat,lon)
#plotSoundingMap(site_list)


