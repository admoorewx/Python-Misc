import numpy as np
import os
import json
import time 
import requests
import matplotlib.pyplot as plt
import xarray
import cartopy
import cartopy.feature as cfeature
import cartopy.crs as ccrs
from herbie import Herbie 
from datetime import datetime, timedelta
from scipy.interpolate import griddata
from matplotlib.colors import LinearSegmentedColormap


# Save directory 
save_dir = "/home/andrew/wxtest/wxtest/static/data/model_error"

# set the number of hours in the past to grab rrfs and SFC data for. 
# This should at least be >= 1 since the absolute latest rrfs and SFC data may not be 
# immediately available 
step_back = 1
################################################################################################
def return_model_data(model,target_time,target_fh,product,variable):
	H = Herbie(
	    target_time,
	    model=model,
	    fxx=target_fh,
	    product="testbed.conus", 
	    member=1
	)
	return ds
################################################################################################
def C2F(values):
	# (K − 273.15) × 9/5 + 32 = F
	try:
		return values * (9.0/5.0) + 32.0
	except:
		return np.asarray(values) * (9.0/5.0) + 32.0
################################################################################################

################################################################################################
############# SURFACE OBS ##################
synoptic_api_root = "https://api.synopticdata.com/v2/"
synoptic_data_token = ""
api_request_url = os.path.join(synoptic_api_root,"stations/nearesttime")
obs_timestamp = (datetime.utcnow()-timedelta(hours=step_back)).strftime("%Y%m%d%H00")
api_arguments = {"token":synoptic_data_token,
				 "attime":obs_timestamp,
				 "within":30,
				 "country":"us",
				 "var":"air_temp,dew_point_temperature"
				 }
req = requests.get(api_request_url, params=api_arguments)
data = req.json()
# Organize the surface obs data
temps = []
dewps = []
t_stids = []
d_stids = []
t_lonlats = []
d_lonlats = []
air_temp_keys = ['air_temp_value_1','air_temp_value_2','air_temperature_1']
dewp_keys = ['dew_point_temperature_value_1d']
for station in data['STATION']:
	# for key,value in station.items():
	# 	print(key,value)
	lat = float(station['LATITUDE'])
	lon = float(station['LONGITUDE'])
	lonlat = [lon,lat]
	# Get the temperature data first 
	for key,obj in station['OBSERVATIONS'].items():
		if key in air_temp_keys:
			temp = float(obj['value'])
			t_stids.append(station['STID'])
			t_lonlats.append(lonlat)
			temps.append(temp)
		if key in dewp_keys:
			dewp = float(obj['value'])
			d_stids.append(station['STID'])
			d_lonlats.append(lonlat)
			dewps.append(dewp)

# Convert temps/dewps from C to F
temps = C2F(temps)
dewps = C2F(dewps)


######################## rrfs #################################
# Using the Herbie package to download the model data 
# Get the target date/time and set desired params
date_timestamp = (datetime.utcnow()-timedelta(hours=step_back)).strftime("%Y-%m-%d %H")
target_hour = 0
sfc_temp = "TMP:2 m above"
sfc_dewp = "DPT:2 m above"
sfc_ttd = ":(?:TMP|DPT):2 m"
product = "sfc"

# rrfs Sfc temps/dewpoints
rrfs_sfc = return_model_data("rrfs",date_timestamp,target_hour,product,sfc_ttd)
rrfs_lat = rrfs_sfc.variables['latitude'].values
rrfs_lon = rrfs_sfc.variables['longitude'].values
rrfs_lon = rrfs_lon - 360.0 # convert from eastings to westings
rrfs_temps = rrfs_sfc.variables['t2m'].values
rrfs_dewps = rrfs_sfc.variables['d2m'].values
latlons = list(zip(rrfs_lon.flatten(),rrfs_lat.flatten()))
rrfs_temps = rrfs_temps.flatten() - 273.15 # convert from K to C 
rrfs_temps = C2F(rrfs_temps) # Convert from C to F
rrfs_dewps = rrfs_dewps.flatten() - 273.15 # convert from K to C 
rrfs_dewps = C2F(rrfs_dewps) # Convert from C to F

rrfs_station_temps = griddata(latlons,rrfs_temps,t_lonlats,method='linear')
# Find the difference with the observed temperatures
rrfs_temp_diff = rrfs_station_temps - temps

rrfs_station_dewps = griddata(latlons,rrfs_dewps,d_lonlats,method='linear')
# Find the difference with the observed temperatures
rrfs_dewp_diff = rrfs_station_dewps - dewps

# Filter out the Nan values for stations outside of the domain 
inds = np.where(np.isnan(rrfs_station_temps) == False)[0]
t_lonlats = np.asarray(t_lonlats)[inds]
t_lons = [t_lonlats[i][0] for i in range(0,len(t_lonlats))]
t_lats = [t_lonlats[i][1] for i in range(0,len(t_lonlats))]
# Get the values to plot 
t_error = np.asarray(rrfs_temp_diff)[inds]

# Filter out the Nan values for stations outside of the domain 
dinds = np.where(np.isnan(rrfs_station_dewps) == False)[0]
d_lonlats = np.asarray(d_lonlats)[dinds]
d_lons = [d_lonlats[i][0] for i in range(0,len(d_lonlats))]
d_lats = [d_lonlats[i][1] for i in range(0,len(d_lonlats))]
# Get the values to plot 
d_error = np.asarray(rrfs_dewp_diff)[dinds]


# Create a scatter plot image for the temperature errors
fig = plt.figure(figsize=(12, 9)) # figsize=(4, 4)
#ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], projection=ccrs.Mercator(central_longitude=-75.0)) #ccrs.PlateCarree()) 
ax = plt.axes(projection=ccrs.Mercator(central_longitude=-75.0)) 
ax.add_feature(cartopy.feature.OCEAN, zorder=0, facecolor='darkslategray')
ax.add_feature(cartopy.feature.LAKES, facecolor='darkslategray',edgecolor='none')
ax.add_feature(cartopy.feature.BORDERS, edgecolor='k',linewidth=0.75)
# Add hi-res states
scale = '110m'
states50 = cfeature.NaturalEarthFeature(
    category='cultural',
    name='admin_1_states_provinces_lines',
    scale=scale,
    facecolor='none',
    edgecolor='k')
ax.add_feature(states50, zorder=2, linewidth=0.7)
# add hi-res coastline (for islands)
#ax.coastlines(resolution='50m', color='k', linewidth=1)
# add hi-res land cover
land_10m = cartopy.feature.NaturalEarthFeature('physical', 'land', '10m')
ax.add_feature(land_10m, zorder=0, facecolor='gray', edgecolor='k', linewidth=0.75)
# change the extent
ax.set_extent([-127., -65., 23., 49.])
scat = ax.scatter(t_lons,t_lats,c=t_error,s=12.0,cmap="RdBu_r", vmin=-10, vmax=10, edgecolor='none',alpha=0.5, transform=ccrs.PlateCarree())
fig.colorbar(scat, ax=ax, orientation='horizontal',label='Error (F)',shrink=0.75,pad=0.02)
meta_timestamp = (datetime.utcnow()-timedelta(hours=1)).strftime("%m/%d/%Y %H UTC")
ax.set_title(f'rrfs Temperature Initialization Error\nValid {meta_timestamp}')
plt.tight_layout()
# File creation time, convert to datetime object
plt.savefig(os.path.join(save_dir,"rrfs_temp_error.png"))

# Create a scatter plot image for the dewpoint errors
fig = plt.figure(figsize=(12, 9)) # figsize=(4, 4)
#ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], projection=ccrs.Mercator(central_longitude=-75.0)) #ccrs.PlateCarree()) 
ax = plt.axes(projection=ccrs.Mercator(central_longitude=-75.0)) 
ax.add_feature(cartopy.feature.OCEAN, zorder=0, facecolor='darkslategray')
ax.add_feature(cartopy.feature.LAKES, facecolor='darkslategray',edgecolor='none')
ax.add_feature(cartopy.feature.BORDERS, edgecolor='k',linewidth=0.75)
# Add hi-res states
scale = '110m'
states50 = cfeature.NaturalEarthFeature(
    category='cultural',
    name='admin_1_states_provinces_lines',
    scale=scale,
    facecolor='none',
    edgecolor='k')
ax.add_feature(states50, zorder=2, linewidth=0.7)
# add hi-res coastline (for islands)
#ax.coastlines(resolution='50m', color='k', linewidth=1)
# add hi-res land cover
land_10m = cartopy.feature.NaturalEarthFeature('physical', 'land', '10m')
ax.add_feature(land_10m, zorder=0, facecolor='gray', edgecolor='k', linewidth=0.75)
# change the extent
ax.set_extent([-127., -65., 23., 49.])
scat = ax.scatter(d_lons,d_lats,c=d_error,s=12.0,cmap="RdYlGn", vmin=-10, vmax=10, edgecolor='none',alpha=0.5, transform=ccrs.PlateCarree())
fig.colorbar(scat, ax=ax, orientation='horizontal',label='Error (F)',shrink=0.75,pad=0.02)
meta_timestamp = (datetime.utcnow()-timedelta(hours=1)).strftime("%m/%d/%Y %H UTC")
ax.set_title(f'rrfs Dewpoint Initialization Error\nValid {meta_timestamp}')
plt.tight_layout()
# File creation time, convert to datetime object
plt.savefig(os.path.join(save_dir,"rrfs_dewp_error.png"))
