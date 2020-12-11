from scipy.interpolate import griddata
from netCDF4 import Dataset
import numpy as np

import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

DataDirectory = 'H:\\Research\\STP\\' # Path to where your metar data is stored
outdir = 'H:\\Research\\' # directory where you want output images to be saved to
filename = 'sfcoalite_15062500.nc'
lat_list = [35.0,43.0]
lon_list = [-96.0,-97.1]

#######################################################################################################################
def getMesoValue(DataDirectory,filename,lat,lon):
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

    STPF0 = griddata( points, STPF, (lon,lat) )
    STPE0 = griddata(points, STPE, (lon, lat))

    print(STPF0,STPE0)


def getMesoValues(DataDirectory,filename,lat_list,lon_list):
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


def plotSTP(DataDirectory,filename):
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

    plt.title("RAP SFC OA Fixed-Layer STP valid at "+filename[12:14]+"/"+filename[14:16]+"/"+filename[10:12]+" "+filename[16:18]+" UTC")
    plt.colorbar(ticks=np.arange(0,10,1), label="STP Value")
    ax.set_aspect('auto', adjustable=None)

    plt.show()




#stpe_list, stpf_list = getMesoValues(DataDirectory,filename, lat_list, lon_list)
#plotSTP(DataDirectory,filename)