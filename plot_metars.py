# Map plotting imports
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import cartopy.io.shapereader as shpreader
# Utility imports
import os
import urllib
import xarray as xr
import datetime
# Metpy imports
from metpy.calc import reduce_point_density
from metpy.io import metar
from metpy.plots import current_weather, sky_cover, StationPlot,  colortables
from metpy.plots import add_timestamp




def cleanOut(saveTo):
    # Clean out the previous data
    for filename in os.listdir(saveTo):
      if filename.startswith("compRefl"):
        os.remove(saveTo+"\\"+filename)
      elif filename.startswith("metpy_metars"):
        os.remove(saveTo+"\\"+filename)


def roundTime(dt=None, roundTo=60):
   """Round a datetime object to any time lapse in seconds
   dt : datetime.datetime object, default now.
   roundTo : Closest number of seconds to round to, default 1 minute.
   Author: Thierry Husson 2012 - Use it as you want but don't blame me.
   """
   if dt == None : dt = datetime.datetime.now()
   seconds = (dt.replace(tzinfo=None) - dt.min).seconds
   rounding = (seconds+roundTo/2) // roundTo * roundTo
   return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)


def getDates():
    # Get current date and time
    # Returns two date strings in YearMonthDate_HourMin format:
    # 1) radar datetime
    # 2) surface obs datetime
    now = datetime.datetime.utcnow()
    radar_now = roundTime(now,300) # round the current time to the nearest 5 min
    obs_now = roundTime(now,3600) # round the current time to the nearest hour
    radar_date = datetime.datetime.strftime(radar_now,"%Y%m%d%H%M")
    obs_date = datetime.datetime.strftime(obs_now,"%Y%m%d_%H%M")
    return radar_date, obs_date

def roundRadTimeDown(radar_date):
    # radar_date is a string in the format "%Y%m%d%H%M"
    # This function will round this number down by 5 minutes
    radar_now = datetime.datetime.strptime(radar_date,"%Y%m%d%H%M")
    new_time = radar_now - datetime.timedelta(seconds=300)
    return datetime.datetime.strftime(new_time,"%Y%m%d%H%M")

def metpyMetars(obs_date):
    # Function: Retrieves most recent metar data from the unidata file server
    # and returns a dataframe (?) of metar data ready for plotting with Metpy.
    # Needs an obs_date (string) in the format of YearMonthDay_HourMinute to retrieve obs.
    saveTo = os.getcwd()
    obsURL = "https://thredds-test.unidata.ucar.edu/thredds/fileServer/noaaport/text/metar/metar_" + obs_date + ".txt"
    urllib.request.urlretrieve(obsURL, saveTo + "\\metpy_metars.txt")
    data = metar.parse_metar_file(saveTo + "\\metpy_metars.txt")
    # Drop rows with missing winds
    data = data.dropna(how='any', subset=['wind_direction', 'wind_speed'])
    os.remove(saveTo+"\\metpy_metars.txt")
    return data


def getCompositeRefl(radar_date):
    # Function: Retrieves the most recent CONUS composite reflectivity image from the IA State mesonet server.
    # This function will download a netCDF file of the radar data and save it locally, read in the data, and parse it
    # through Metpy. Returns an array of lons (x), lats (y), and radar data (dat) ready for plotting.
    try: # first try the rounded up radar time:
        radarURL = "https://mesonet.agron.iastate.edu/cgi-bin/request/raster2netcdf.py?dstr=" + radar_date + "&prod=composite_n0q"
        urllib.request.urlretrieve(radarURL, "compRefl.nc")
    except: # Then try the rounded down time
        radar_date = roundRadTimeDown(radar_date)
    # get the radar data
    ds = xr.open_dataset("compRefl.nc")
    x = ds.variables['lon'][:]
    y = ds.variables['lat'][:]
    dat = ds.metpy.parse_cf('composite_n0q')
    ds.close()
    return x,y,dat



def plot_metar_refl(lllat,lllon,urlat,urlon,obsDensity=None,states=True,counties=True):

    if obsDensity is None: obsDensity = 100000.0 # 100 km by default
    # get the current working directory
    saveTo = os.getcwd()
    # First get the current times for the radar and metar data
    radar_date,obs_date = getDates()
    # Now get the metar data
    data = metpyMetars(obs_date)
    # Now get the radar reflectivity data
    x, y, dat = getCompositeRefl(radar_date)

    # Set up the map projection
    proj = ccrs.LambertConformal(central_longitude=-97.5, central_latitude=34,
                                 standard_parallels=[35])
    # Use the Cartopy map projection to transform station locations to the map and
    # then refine the number of stations plotted by setting a 100km radius
    point_locs = proj.transform_points(ccrs.PlateCarree(), data['longitude'].values,
                                       data['latitude'].values)
    data = data[reduce_point_density(point_locs, obsDensity)]


    # Read in the state shapefiles
    if states:
        state_reader = shpreader.Reader(saveTo+'\\shapefiles\\ne_10m_admin_1_states_provinces.shp')
        good_states = list(state_reader.geometries())
        GOOD_STATES = cfeature.ShapelyFeature(good_states, ccrs.PlateCarree())
    # Read in the county shapefiles
    if counties:
        reader = shpreader.Reader(saveTo+'\\shapefiles\\tl_2017_us_county.shp')
        counties = list(reader.geometries())
        COUNTIES = cfeature.ShapelyFeature(counties, ccrs.PlateCarree())


    fig = plt.figure(figsize=(20, 20))
    ax = fig.add_subplot(1, 1, 1, projection=dat.metpy.cartopy_crs)
    ax.background_patch.set_facecolor('lightsteelblue')
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), zorder=1)
    ax.add_feature(COUNTIES, facecolor='lightgray', edgecolor='k', alpha=0.9, zorder=2)
    ax.add_feature(GOOD_STATES, facecolor='lightgray', edgecolor='k',alpha=0.9, zorder=3)
    ax.add_feature(cfeature.LAKES, facecolor='lightsteelblue', alpha=0.95, zorder=4)

    # set the extent
    ax.set_extent((lllon, urlon, lllat, urlat))

    #add_metpy_logo(fig, 125, 145)

    ### Plotting the Radar Data ####
    # Set the color map here:
    wv_norm, wv_cmap = colortables.get_with_range('NWSReflectivity', 0, 80)
    wv_cmap.set_under('k')
    # plot the radar data
    im = ax.imshow(dat[:], cmap=wv_cmap, norm=wv_norm,
                   extent=(x.min(), x.max(), y.min(), y.max()), zorder=5, alpha=0.40)


    #### Plotting the surface obs ####
    # Start the station plot by specifying the axes to draw on, as well as the
    # lon/lat of the stations (with transform). We also the fontsize to 12 pt.
    stationplot = StationPlot(ax, data['longitude'].values, data['latitude'].values,
                              clip_on=True, transform=ccrs.PlateCarree(), fontsize=12)
    # Plot the temperature and dew point to the upper and lower left, respectively, of
    # the center point. Each one uses a different color.
    stationplot.plot_barb(data['eastward_wind'].values, data['northward_wind'].values,zorder=10.0)
    stationplot.plot_parameter('NW', ((data['air_temperature'].values * 1.8) + 32.0), color='red')
    stationplot.plot_parameter('SW', ((data['dew_point_temperature'].values * 1.8) + 32.0),
                               color='darkgreen')
    stationplot.plot_parameter('NE', data['air_pressure_at_sea_level'].values,formatter=lambda v: format(10 * v, '.0f')[-3:])
    stationplot.plot_symbol('C', data['cloud_coverage'].values, sky_cover)
    stationplot.plot_symbol('W', data['present_weather'].values, current_weather)

    plotTime = roundTime(datetime.datetime.utcnow(),300)
    add_timestamp(ax, plotTime, y=0.96, fontsize=20, high_contrast=True,zorder=10)

    plt.show()
    #plt.savefig(saveTo+"metar_refl_"+radar_date+".png")
    #cleanOut(saveTo)


def plot_metar(lllat,lllon,urlat,urlon,obsDensity=None,states=True,counties=True):

    if obsDensity is None: obsDensity = 100000.0 # 100 km by default
    # get the current working directory
    saveTo = os.getcwd()
    # First get the current times for the radar and metar data
    # note that we won't use the radar_date here
    radar_date,obs_date = getDates()
    # Now get the metar data
    data = metpyMetars(obs_date)

    # Set up the map projection
    proj = ccrs.LambertConformal(central_longitude=-97.5, central_latitude=34,
                                 standard_parallels=[35])
    # Use the Cartopy map projection to transform station locations to the map and
    # then refine the number of stations plotted by setting a 100km radius
    point_locs = proj.transform_points(ccrs.PlateCarree(), data['longitude'].values,
                                       data['latitude'].values)
    data = data[reduce_point_density(point_locs, obsDensity)]


    # Read in the state shapefiles
    if states:
        state_reader = shpreader.Reader(saveTo+'\\shapefiles\\ne_10m_admin_1_states_provinces.shp')
        good_states = list(state_reader.geometries())
        GOOD_STATES = cfeature.ShapelyFeature(good_states, ccrs.PlateCarree())
    # Read in the county shapefiles
    if counties:
        reader = shpreader.Reader(saveTo+'\\shapefiles\\tl_2017_us_county.shp')
        counties = list(reader.geometries())
        COUNTIES = cfeature.ShapelyFeature(counties, ccrs.PlateCarree())


    fig = plt.figure(figsize=(20, 20))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.background_patch.set_facecolor('lightsteelblue')
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), zorder=1)
    ax.add_feature(COUNTIES, facecolor='lightgray', edgecolor='k', alpha=0.9, zorder=2)
    ax.add_feature(GOOD_STATES, facecolor='lightgray', edgecolor='k',alpha=0.9, zorder=3)
    ax.add_feature(cfeature.LAKES, facecolor='lightsteelblue', alpha=0.95, zorder=4)

    # set the extent
    ax.set_extent((lllon, urlon, lllat, urlat))

    #add_metpy_logo(fig, 125, 145)

    #### Plotting the surface obs ####
    # Start the station plot by specifying the axes to draw on, as well as the
    # lon/lat of the stations (with transform). We also the fontsize to 12 pt.
    stationplot = StationPlot(ax, data['longitude'].values, data['latitude'].values,
                              clip_on=True, transform=ccrs.PlateCarree(), fontsize=12)
    # Plot the temperature and dew point to the upper and lower left, respectively, of
    # the center point. Each one uses a different color.
    stationplot.plot_barb(data['eastward_wind'].values, data['northward_wind'].values,zorder=10.0)
    stationplot.plot_parameter('NW', ((data['air_temperature'].values * 1.8) + 32.0), color='red')
    stationplot.plot_parameter('SW', ((data['dew_point_temperature'].values * 1.8) + 32.0),
                               color='darkgreen')
    stationplot.plot_parameter('NE', data['air_pressure_at_sea_level'].values,formatter=lambda v: format(10 * v, '.0f')[-3:])
    stationplot.plot_symbol('C', data['cloud_coverage'].values, sky_cover)
    stationplot.plot_symbol('W', data['present_weather'].values, current_weather)

    plotTime = roundTime(datetime.datetime.utcnow(),300)
    add_timestamp(ax, plotTime, y=0.96, fontsize=20, high_contrast=True,zorder=10)

    plt.show()
    #plt.savefig(saveTo+"metar_"+obs_date+".png")
    #cleanOut(saveTo)



def plot_refl(lllat,lllon,urlat,urlon,states=True,counties=True):
    # get the current working directory
    saveTo = os.getcwd()
    # First get the current times for the radar and metar data (obs_date won't be used)
    radar_date,obs_date = getDates()
    # Now get the radar reflectivity data
    x, y, dat = getCompositeRefl(radar_date)

    # Set up the map projection
    proj = ccrs.LambertConformal(central_longitude=-97.5, central_latitude=34,
                                 standard_parallels=[35])

    # Read in the state shapefiles
    if states:
        state_reader = shpreader.Reader(saveTo+'\\shapefiles\\ne_10m_admin_1_states_provinces.shp')
        good_states = list(state_reader.geometries())
        GOOD_STATES = cfeature.ShapelyFeature(good_states, ccrs.PlateCarree())
    # Read in the county shapefiles
    if counties:
        reader = shpreader.Reader(saveTo+'\\shapefiles\\tl_2017_us_county.shp')
        counties = list(reader.geometries())
        COUNTIES = cfeature.ShapelyFeature(counties, ccrs.PlateCarree())


    fig = plt.figure(figsize=(20, 20))
    ax = fig.add_subplot(1, 1, 1, projection=dat.metpy.cartopy_crs)
    ax.background_patch.set_facecolor('lightsteelblue')
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), zorder=1)
    ax.add_feature(COUNTIES, facecolor='lightgray', edgecolor='k', alpha=0.9, zorder=2)
    ax.add_feature(GOOD_STATES, facecolor='lightgray', edgecolor='k',alpha=0.9, zorder=3)
    ax.add_feature(cfeature.LAKES, facecolor='lightsteelblue', alpha=0.95, zorder=4)

    # set the extent
    ax.set_extent((lllon, urlon, lllat, urlat))

    #add_metpy_logo(fig, 125, 145)

    ### Plotting the Radar Data ####
    # Set the color map here:
    wv_norm, wv_cmap = colortables.get_with_range('NWSReflectivity', 0, 80)
    wv_cmap.set_under('k')
    # plot the radar data
    im = ax.imshow(dat[:], cmap=wv_cmap, norm=wv_norm,
                   extent=(x.min(), x.max(), y.min(), y.max()), zorder=5, alpha=0.40)

    plotTime = roundTime(datetime.datetime.utcnow(),300)
    add_timestamp(ax, plotTime, y=0.96, fontsize=20, high_contrast=True,zorder=10)

    plt.show()
    #plt.savefig(saveTo+"metar_refl_"+radar_date+".png")
    #cleanOut(saveTo)



start = datetime.datetime.now()
plot_metar_refl(23,-127,48,-65)
finish = datetime.datetime.now()
print("Elapsed:")
print(finish-start)
#plot_metar(30,-109,39,-90)
#plot_refl(30,-109,39,-90)