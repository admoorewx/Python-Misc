import csv
import math
import numpy as np
import matplotlib.pyplot as plt
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy.interpolate import griddata
from netCDF4 import Dataset


# For home computer
#DataDirectory = 'H:\\Research\\STP\\' # Path to where your metar data is stored
#outdir = 'H:\\Research\\' # directory where you want output images to be saved to
filename = 'STP_soundings.csv'

# For my laptop
DataDirectory = 'C:\\Users\\admoo\\Desktop\\Projects\\'
NCdir = 'C:\\Users\\admoo\\Desktop\\Projects\\sfcoalite_data\\'
outdir = DataDirectory


#######################################################################################################################
def getMesoValues(DataDirectory,filename,lat_list,lon_list):
    try:
        # first read in the file
        data = Dataset(DataDirectory+filename)
        lats = data.variables['lats'][:]
        lons = data.variables['lons'][:]
        stpf = data.variables['SIGT'][:] # Fixed layer STP
        stpe = data.variables['STPC'][:] # Eff. Layer STP
        # then interpolate to find the most approx value
        points = np.array( (lons.flatten(), lats.flatten()) ).T
        STPF = stpf.flatten()
        STPE = stpe.flatten()

        stpe_list = []
        stpf_list = []

        for l,L in enumerate(lat_list):
            STPF0 = griddata(points, STPF, (lon_list[l],L))
            STPE0 = griddata(points, STPE, (lon_list[l], L))
            stpe_list.append(STPE0)
            stpf_list.append(STPF0)

        return stpe_list, stpf_list

    except:
        filename = filename[0:18]+".nc"
        # first read in the file
        data = Dataset(DataDirectory + filename)
        lats = data.variables['lats'][:]
        lons = data.variables['lons'][:]
        stpf = data.variables['SIGT'][:]  # Fixed layer STP
        stpe = data.variables['STPC'][:]  # Eff. Layer STP
        # then interpolate to find the most approx value
        points = np.array((lons.flatten(), lats.flatten())).T
        STPF = stpf.flatten()
        STPE = stpe.flatten()

        stpe_list = []
        stpf_list = []

        for l, L in enumerate(lat_list):
            STPF0 = griddata(points, STPF, (lon_list[l], L))
            STPE0 = griddata(points, STPE, (lon_list[l], L))
            stpe_list.append(STPE0)
            stpf_list.append(STPF0)

        return stpe_list, stpf_list

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

    print("Read-In Complete!")
    #print(datetime.datetime.now())
    #print("")
    return date, site, lat, lon, stpe, stpf


def plotSTPerrorDist(stpe,stpf):

    stpe = np.asarray(stpe)
    stpf = np.asarray(stpf)

    bins = np.arange(-10,10,0.1)
    hist,bin_edge = np.histogram(stpe,bins,(-10.0,10.0))
    ymax = np.max(hist) + 10
    yloc = ymax - 10
    xloc = 0.5

    plt.figure(1)
    plt.subplot(1,2,1)
    plt.hist(stpe, bins=bins, density=False, align='left', rwidth=0.75, color='steelblue')
    plt.title("Effective Layer STP Error Distribution",fontsize=10)
    plt.xlabel("Error")
    plt.ylabel("Frequency")
    plt.xlim(-6.0, 6.0)
    plt.xticks(np.arange(-6,6,1))
    plt.ylim(0,ymax)
    plt.text(xloc,yloc,"Mean = "+str(round(np.mean(stpe),2)))
    plt.text(xloc,yloc-5,"St. Dev = "+str(round(np.std(stpe),2)))
    plt.text(xloc,yloc-10,"RMSD ="+str(round(np.sqrt(np.mean(stpe**2.0)),2)))
    plt.grid(color='gray',alpha=0.65)

    plt.subplot(1,2,2)
    plt.hist(stpf, bins=bins, density=False, align='left', rwidth=0.75, color='steelblue')
    plt.title("Fixed Layer STP Error Distribution",fontsize=10)
    plt.xlabel("Error")
    plt.xlim(-6., 6)
    plt.xticks(np.arange(-6., 6., 1))
    plt.ylim(0,ymax)
    plt.text(xloc,yloc,"Mean = "+str(round(np.mean(stpf),2)))
    plt.text(xloc,yloc-5,"St. Dev = "+str(round(np.std(stpf),2)))
    plt.text(xloc,yloc-10,"RMSD ="+str(round(np.sqrt(np.mean(stpf**2.0)),2)))
    plt.grid(color='gray',alpha=0.65)

    plt.show()
    #plt.savefig(outdir + "\\Blizzard_SnowAccumHist.png")


    plt.figure(2)
    plt.boxplot([stpe,stpf], labels=["Effective Layer", "Fixed Layer"])
    plt.title("STP Error Distribution \n n = "+str(len(stpe)),fontsize=10)
    plt.ylabel("STP Error Value")
    plt.ylim(-6.0,6.0)

    plt.show()





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


def errorByValue(eff_vals,eff_error,fix_vals,fix_error):

    plt.scatter(eff_vals,eff_error,marker='x',color='r',label="Eff. Layer")
    plt.scatter(fix_vals,fix_error,marker='x',color='b',label="Fixed Layer")
    plt.grid(color='gray',alpha=0.65)
    plt.xlim(0,14)
    plt.xticks(np.arange(0, 14, 1))
    plt.ylim(-6,6)
    plt.ylabel("STP Error")
    plt.xlabel("Observed STP Value")
    plt.title("STP Error by Observed Value")
    plt.legend()
    plt.show()



def sortSites(sites,lat,lon):
    # Used for plotting the spatial distribution of soundings (# of soundings per site)
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


def plotOvM(obsE,mesoE,obsF,mesoF):

    plt.figure(1)
    limit = 13
    linex = np.arange(0,limit+1,1)
    liney = linex
    plt.scatter(obsE,mesoE,marker='x',color='r',label='Effective STP')
    plt.scatter(obsF,mesoF,marker='x',color='b',label="Fixed Layer STP")
    plt.plot(linex,liney,color='k')
    plt.xlim(0,limit)
    plt.ylim(0,limit)
    plt.grid(color='gray',alpha=0.75)
    plt.legend()
    plt.ylabel("SPC Mesoanalysis STP")
    plt.xlabel("Observed Sounding STP")
    plt.title("Observed VS. SPC Mesoanalysis STP")
    plt.show()

    plt.figure(2)
    limit = 3
    linex = np.arange(0,limit+1,1)
    liney = linex
    plt.scatter(obsE,mesoE,marker='x',color='r',label='Effective STP')
    plt.scatter(obsF,mesoF,marker='x',color='b',label="Fixed Layer STP")
    plt.plot(linex,liney,color='k')
    plt.xlim(0,limit)
    plt.ylim(0,limit)
    plt.grid(color='gray',alpha=0.75)
    plt.legend()
    plt.ylabel("SPC Mesoanalysis STP")
    plt.xlabel("Observed Sounding STP")
    plt.title("Observed VS. SPC Mesoanalysis STP")
    plt.show()



def plotSTP(DataDirectory,filename,sites=None):
    ### Set up the map ###
    ax = plt.axes(projection=ccrs.PlateCarree())
    #ax.add_feature(cartopy.feature.LAND)
    #ax.add_feature(cartopy.feature.OCEAN)
    #ax.add_feature(cartopy.feature.STATES, edgecolor='gray')
    #ax.add_feature(cartopy.feature.COASTLINE)

    # add lakes and international borders
    ax.add_feature(cartopy.feature.LAKES)
    ax.add_feature(cartopy.feature.BORDERS)

    # Add hi-res states
    scale = '110m'
    states50 = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_1_states_provinces_lines',
        scale=scale,
        facecolor='none',
        edgecolor='black')
    ax.add_feature(states50, zorder=2, linewidth=1)

    # add hi-res coastline (for islands)
    ax.coastlines(resolution='50m', color='black', linewidth=1)
    # add hi-res land cover
    land_10m = cartopy.feature.NaturalEarthFeature('physical', 'land', '10m')
    ax.add_feature(land_10m, zorder=0, facecolor='white', edgecolor='white', linewidth=1)
    # change the extent
    ax.set_extent([-125, -65, 23, 50])

    ### Plot the data ###
    data = Dataset(DataDirectory+filename)
    lats = data.variables['lats'][:]
    lons = data.variables['lons'][:]
    stpf = data.variables['SIGT'][:] # Fixed layer STP
    stpe = data.variables['STPC'][:] # Eff. Layer STP

    plt.contourf(lons, lats, stpe, np.arange(0.1,10,0.1),
                 cmap='nipy_spectral',
                 alpha=0.95,
                 transform=ccrs.PlateCarree())

    plt.title("RAP SFC OA Effective Layer STP valid at "+filename[12:14]+"/"+filename[14:16]+"/"+filename[10:12]+" "+filename[16:18]+" UTC")
    plt.colorbar(ticks=np.arange(0,10,1), label="STP Value")
    ax.set_aspect('auto', adjustable=None)

    if sites is not None:
        for s in range(0,len(sites[0])):
            name = sites[0][s]
            lat = sites[1][s]
            lon = sites[2][s]
            val = round(float(sites[3][s]),2)
            plt.plot(lon, lat, markersize=3, marker='o', color='k')
            plt.text(lon, lat+0.5, name+": "+str(val),
                     horizontalalignment='center',
                     transform=ccrs.PlateCarree(),
                     fontsize=10,
                     weight='bold')

    plt.show()






def sortByDate(date, lat, lon, stpe, stpf, site):
    # This will read in the data and organize it such that
    # each date contains all lat/lon points, values, and site IDs
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
            files[date_string][2].append(stpe[d])
            files[date_string][3].append(stpf[d])
            files[date_string][4].append(site[d])
        else:
            files[date_string] = [[lat[d]],[lon[d]],[stpe[d]],[stpf[d]],[site[d]]]
    return files

date, site, lat, lon, stpe, stpf = dataReadIn(DataDirectory,filename)
#plotTemporalDist(date)
#plotSTPDist(stpe,stpf)
#site_list = sortSites(site,lat,lon)
#plotSoundingMap(site_list)

obsE = []
obsF = []
mesoE = []
mesoF = []
files = sortByDate(date, lat, lon, stpe, stpf, site)

# I'm not super thrilled about this methodology right now.
# It feels kinda sloppy and I'm not convinced there isn't some mix-matching going on.
# Try to find a more robust way to get the meso data AND match it to the corresponding obs.

eff_errors = []
fix_errors = []
for key, values in files.items():

    stpe_diff = []
    stpf_diff = []

    Mstpe, Mstpf = getMesoValues(NCdir,"sfcoalite_"+key+".nc",values[0],values[1])

    # For testing
    # mini_sites = [values[4], values[0], values[1], Mstpe]
    # print(key)
    # print(values[4])
    # print(values[2])
    # print(Mstpe)
    # plotSTP(NCdir,"sfcoalite_"+key+".nc",sites=mini_sites)

    for val in range(0,len(Mstpe)):
        mesoE.append(Mstpe[val])
        mesoF.append(Mstpf[val])
        obsE.append(values[2][val])
        obsF.append(values[3][val])
        stpe_err = Mstpe[val] - values[2][val]
        stpf_err = Mstpf[val] - values[3][val]
        stpe_diff.append(stpe_err)
        stpf_diff.append(stpf_err)
        eff_errors.append(stpe_err)
        fix_errors.append(stpf_err)


    # for i in range(0,len(values[0])):
    #     stpe_err = values[2][i] - Mstpe[i]
    #     stpf_err = values[3][i] - Mstpf[i]
    #     stpe_diff.append(stpe_err)
    #     stpf_diff.append(stpf_err)
    #     eff_errors.append(stpe_err)
    #     fix_errors.append(stpf_err)

    files[key] = [values[0], values[1], values[2], values[3], values[4], Mstpe, Mstpf, stpe_diff, stpf_diff]

#print(len(obsE),len(mesoE))

#plotOvM(obsE,obsF,mesoE,mesoF)
eff_errors = [x for x in eff_errors if (x < 100.0) and (x > -100.0)] # These filters are here as a quick fix
fix_errors = [y for y in fix_errors if (y < 100.0) and (y > -100.0)] # since the KEY sounding is out of the meso bounds and returns an invalid #.

plotSTPerrorDist(eff_errors,fix_errors)
#errorByValue(obsE,eff_errors,obsF,fix_errors)

