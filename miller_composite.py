from datetime import datetime, timedelta

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.lines as lines
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import metpy.calc as mpcalc
import numpy as np
import numpy.ma as ma

from metpy.units import units
from netCDF4 import num2date
from scipy.ndimage import gaussian_filter
from siphon.catalog import TDSCatalog

# Specify our date/time of product desired
dt = datetime.utcnow()

# Construct the URL for our THREDDS Data Server Catalog,
# and access our desired dataset within via NCSS
# base_url = 'https://www.ncei.noaa.gov/thredds/model-namanl-old/'
# cat = TDSCatalog(f'{base_url}{dt:%Y%m}/{dt:%Y%m%d}/catalog.xml')
# ncss = cat.datasets[f'namanl_218_{dt:%Y%m%d}_{dt:%H}00_000.grb'].subset()

# Setting to get the latest RAP instead
rap_url = 'https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RAP/CONUS_13km/latest.xml'
cat = TDSCatalog(rap_url)
ncss = cat.datasets[0].subset()


# for var in ncss.variables:
#         print(var)
#exit()
# Create our NCSS query with desired specifications
query = ncss.query()
query.all_times()
query.add_lonlat()
query.lonlat_box(-135, -60, 15, 65).time(datetime.utcnow())
query.variables('Geopotential_height_isobaric',
                'u-component_of_wind_isobaric',
                'v-component_of_wind_isobaric',
                'Temperature_isobaric',
                'Relative_humidity_isobaric',
                'Relative_humidity_height_above_ground',
                'Temperature_height_above_ground',
                'u-component_of_wind_height_above_ground', # 10m U wind
                'v-component_of_wind_height_above_ground', # 10m V wind
                'MSLP_MAPS_System_Reduction_msl')

# Obtain the data we've queried for
data_18z = ncss.get_data(query)

# Assign variable names to collected data
dtime = data_18z.variables['Geopotential_height_isobaric'].dimensions[0]
dlev = data_18z.variables['Geopotential_height_isobaric'].dimensions[1]
lat = data_18z.variables['lat'][:]
lon = data_18z.variables['lon'][:]
lev = units.hPa * (data_18z.variables[dlev][:]/100.0)
times = data_18z.variables[dtime]
vtimes = num2date(times[:].squeeze(), times.units)
temps = data_18z.variables['Temperature_isobaric']
tmp = units.kelvin * temps[0, :]
uwnd = (units.meter / units.second) * data_18z.variables['u-component_of_wind_isobaric'][0, :]
vwnd = (units.meter / units.second) * data_18z.variables['v-component_of_wind_isobaric'][0, :]
u10 = units('m/s') * data_18z.variables['u-component_of_wind_height_above_ground'][0,0, :]
v10 = units('m/s') * data_18z.variables['v-component_of_wind_height_above_ground'][0,0, :]
hgt = units.meter * data_18z.variables['Geopotential_height_isobaric'][0, :]
relh = units.percent * data_18z.variables['Relative_humidity_isobaric'][0, :]
rh_sfc = (units(data_18z.variables['Relative_humidity_height_above_ground'].units) *
          data_18z.variables['Relative_humidity_height_above_ground'][0, 0, :])
tmp_sfc = units.kelvin * data_18z.variables['Temperature_height_above_ground'][0, 0, :]
# Convert surface RH to dewpoint
dewp_sfc = mpcalc.dewpoint_from_relative_humidity(tmp_sfc,rh_sfc)
mslp = units.Pa * data_18z.variables['MSLP_MAPS_System_Reduction_msl'][0,:]

# 300 hPa, index 28
idx_300 = np.where(lev == 300. * units.hPa)[0][0]
u_300 = uwnd[idx_300, :].to('kt')
v_300 = vwnd[idx_300, :].to('kt')

# 500 hPa, index 20
idx_500 = np.where(lev == 500. * units.hPa)[0][0]
u_500 = uwnd[idx_500].to('kt')
v_500 = vwnd[idx_500].to('kt')
hgt_500 = hgt[idx_500]

# 700 hPa, index 12
idx_700 = np.where(lev == 700. * units.hPa)[0][0]
tmp_700 = tmp[idx_700].to('degC')
rh_700 = relh[idx_700]

# 850 hPa, index 6
idx_850 = np.where(lev == 850. * units.hPa)[0][0]
u_850 = uwnd[idx_850].to('kt')
v_850 = vwnd[idx_850].to('kt')

# 10 meter winds
u10 = u10.to('kt')
v10 = v10.to('kt')


wspd_300 = gaussian_filter(mpcalc.wind_speed(u_300, v_300), 5)
wspd_500 = gaussian_filter(mpcalc.wind_speed(u_500, v_500), 5)
wspd_850 = gaussian_filter(mpcalc.wind_speed(u_850, v_850), 5)
wspd_10m = gaussian_filter(mpcalc.wind_speed(u10,v10),5)

Td_dep_700 = tmp_700 - mpcalc.dewpoint_from_relative_humidity(tmp_700, rh_700)

mask_500 = ma.masked_less_equal(wspd_500, 0.66 * np.max(wspd_500)).mask
u_500[mask_500] = np.nan
v_500[mask_500] = np.nan

# 300 hPa
mask_300 = ma.masked_less_equal(wspd_300, 0.66 * np.max(wspd_300)).mask
u_300[mask_300] = np.nan
v_300[mask_300] = np.nan

# 850 hPa
mask_850 = ma.masked_less_equal(wspd_850, 0.66 * np.max(wspd_850)).mask
u_850[mask_850] = np.nan
v_850[mask_850] = np.nan

# 10 m 
mask_10m = ma.masked_less_equal(wspd_10m, 10.0).mask
u10[mask_10m] = np.nan
v10[mask_10m] = np.nan 


# Set up our projection
crs = ccrs.LambertConformal(central_longitude=-100.0, central_latitude=45.0)

# Coordinates to limit map area
bounds = [-122., -75., 25., 50.]


fig = plt.figure(1, figsize=(17, 12))
ax = fig.add_subplot(1, 1, 1, projection=crs)
ax.set_extent(bounds, crs=ccrs.PlateCarree())
ax.coastlines('50m', edgecolor='black', linewidth=0.75)
ax.add_feature(cfeature.STATES, linewidth=0.25)


# Plot surface dewpoint > 55
ax.contourf(lon, lat, dewp_sfc.to('degF'), range(50, 86, 30), alpha=0.3,
            transform=ccrs.PlateCarree(),
            colors=['turquoise'], zorder=2)

# Plot surface dewpoint > 60
ax.contourf(lon, lat, dewp_sfc.to('degF'), range(60, 86, 25), alpha=0.4,
            transform=ccrs.PlateCarree(),
            colors=['green'], zorder=2)

# Plot surface dewpoint > 70
ax.contourf(lon, lat, dewp_sfc.to('degF'), range(70, 86, 15), alpha=0.5,
            transform=ccrs.PlateCarree(),
            colors=['darkorchid'], zorder=2)


# Plot 500-hPa heights
cs500 = ax.contour(lon, lat, hgt_500, range(4600, 6200, 80), alpha=0.5, linewidths=3, linestyles='dashed', transform=ccrs.PlateCarree(),
            colors='blue', zorder=3)
ax.clabel(cs500, cs500.levels, inline=True, fontsize=8)


# Plot MSLP
csmslp = ax.contour(lon,lat,mslp.to('hPa'),range(960,1040,2),alpha=0.6,linewidths=1.0, transform=ccrs.PlateCarree(),colors='k',zorder=2)
ax.clabel(csmslp, csmslp.levels, inline=True, fontsize=8)


# Define a skip to reduce the barb point density
skip_300 = (slice(None, None, 15), slice(None, None, 15))
skip_500 = (slice(None, None, 12), slice(None, None, 12))
skip_850 = (slice(None, None, 10), slice(None, None, 10))
skip_10m = (slice(None, None, 10), slice(None, None, 10))

# 300-hPa wind barbs
# jet300 = ax.barbs(lon[skip_300], lat[skip_300], u_300[skip_300].m, v_300[skip_300].m, length=6,
#                   transform=ccrs.PlateCarree(),
#                   color='firebrick', zorder=10, label='300-hPa Jet Core Winds (kt)')


# 500-hPa wind barbs
jet500 = ax.barbs(lon[skip_500], lat[skip_500], u_500[skip_500].m, v_500[skip_500].m, length=6,
                  transform=ccrs.PlateCarree(),
                  color='b', zorder=9, label='500-hPa Jet Core Winds (kt)')

# 850-hPa wind barbs
jet850 = ax.barbs(lon[skip_850], lat[skip_850], u_850[skip_850].m, v_850[skip_850].m, length=6,
                  transform=ccrs.PlateCarree(),
                  color='firebrick', zorder=8, label='850-hPa Jet Core Winds (kt)')

# 850-hPa wind barbs
jetsfc = ax.barbs(lon[skip_10m], lat[skip_10m], u10[skip_10m].m, v10[skip_10m].m, length=6,
                  transform=ccrs.PlateCarree(),
                  color='k', zorder=8, label='10m wind > 10 kt')

# Legend
turquoise = mpatches.Patch(color='turquoise', label='Surface Td > 50 F')
green = mpatches.Patch(color='green', label='Surface Td > 60 F')
darkorchid = mpatches.Patch(color='darkorchid', label='Surface Td > 70 F')
#tan = mpatches.Patch(color='gray', label='700 hPa Dewpoint Depression > 15 C')
#red_line = lines.Line2D([], [], color='red', label='Best Lifted Index (C)')
black_line = lines.Line2D([], [], linestyle='solid', color='k',
                           label='MSLP (hPa)')
blue_line = lines.Line2D([], [], linestyle='dashed', color='b',
                           label='500-hPa Height (m)')
leg = plt.legend(handles=[jet500,jet850,jetsfc,turquoise,green,darkorchid,black_line,blue_line], loc=3,framealpha=1)
leg.set_zorder(100)
ax.set_title(f'RAP Composite Analysis Valid: {vtimes}',fontsize=18)
plt.savefig("miller_composite.png")