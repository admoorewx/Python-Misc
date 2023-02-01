import os 
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.lines as lines
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import metpy.calc as mpcalc
import metpy.units as units
import numpy as np
import numpy.ma as ma
import xarray
from metpy.units import units
from metpy.plots import StationPlot
from netCDF4 import num2date, Dataset
from datetime import datetime, timedelta
from siphon.catalog import TDSCatalog
from surface_obs_functions import find_closest_time, to_float, clean_data, filter_by_bounds

goes_file_path = "/home/andrew/Research/goes/"
save_path = "/home/andrew/Research/images"

# copied from the browser url box
asos_file = "/home/andrew/Research/surface_obs/asos_20190029_20190030.csv"

for filename in os.listdir(goes_file_path):
	C = xarray.open_dataset(os.path.join(goes_file_path,filename))
	# Scan's start time, converted to datetime object
	scan_start = datetime.strptime(C.time_coverage_start, '%Y-%m-%dT%H:%M:%S.%fZ')

	# Scan's end time, converted to datetime object
	scan_end = datetime.strptime(C.time_coverage_end, '%Y-%m-%dT%H:%M:%S.%fZ')

	# File creation time, convert to datetime object
	file_created = datetime.strptime(C.date_created, '%Y-%m-%dT%H:%M:%S.%fZ')

	# The 't' variable is the scan's midpoint time
	midpoint = str(C['t'].data)[:-8]
	scan_mid = datetime.strptime(midpoint, '%Y-%m-%dT%H:%M:%S.%f')

	R = C['CMI'].data
	dat = C.metpy.parse_cf('CMI')
	geos = dat.metpy.cartopy_crs
	# We also need the x (north/south) and y (east/west) axis sweep of the ABI data
	x = dat.x
	y = dat.y
	extent = [-91.0,-106.0,36.0,45.0]

	### SURFACE OBS ###
	data = find_closest_time(scan_start,asos_file,window=10)
	data = filter_by_bounds(data,extent)
	print(len(data))
	data = clean_data(data)
	tair = to_float(data['tmpf'].values)
	dewp = to_float(data['dwpf'].values)
	lats = to_float(data['lat'].values)
	lons = to_float(data['lon'].values)
	wspd = to_float(data['sknt'].values)
	wdir = to_float(data['drct'].values)


	# Convert wind to components
	u, v = mpcalc.wind_components(wspd * units.knots, wdir * units.degree)

	# Need to handle missing (NaN) and convert to proper code
	# cloud_cover = 8 * data['sky_coverage'] / 100.
	# cloud_cover[np.isnan(cloud_cover)] = 10
	# cloud_cover = cloud_cover.astype(np.int)

	fig = plt.figure(figsize=(15, 12))

	# Create axis with Geostationary projection
	ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
	ax.set_extent(extent, crs=ccrs.PlateCarree())

	# Add the RGB image to the figure. The data is in the same projection as the
	# axis we just created.
	ax.imshow(R, cmap='gist_gray', origin='upper',
	          extent=(x.min(), x.max(), y.min(), y.max()), transform=geos)

	# Add Coastlines and States
	ax.coastlines(resolution='50m', color='black', linewidth=0.25)
	ax.add_feature(ccrs.cartopy.feature.STATES, edgecolor='k', linewidth=1.5)

	plt.title('GOES-16 Ch. 2', loc='left', fontweight='bold', fontsize=15)

	# Create a station plot pointing to an Axes to draw on as well as the location of points
	stationplot = StationPlot(ax, lons, lats, transform=ccrs.PlateCarree(),fontsize=8)
	stationplot.plot_parameter('NW', tair, color='red')
	stationplot.plot_parameter('SW', dewp, color='g')
	# Add wind barbs
	stationplot.plot_barb(u, v, color='white')

	plt.title('{}'.format(scan_start.strftime('%d %B %Y %H:%M UTC ')), loc='right')
	plt.tight_layout()
	plt.savefig(os.path.join(save_path,f'goes_sfc_{datetime.strftime(scan_start,"%Y%m%d%H%MZ")}'))
	plt.close()
	