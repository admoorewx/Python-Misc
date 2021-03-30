import multiprocessing as mp
import time
import concurrent.futures
import matplotlib.pyplot as plt
import pylab
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
from datetime import datetime, timedelta
from siphon.radarserver import RadarServer
import numpy as np
import metpy.plots as mpplots

start = time.perf_counter()


# Method 1
# if __name__ == '__main__':
#     process1 = multiprocessing.Process(target=sleeping)
#     process2 = multiprocessing.Process(target=sleeping)
#     process1.start()
#     process2.start()
#     process1.join()
#     process2.join()

# Method 2
# processes = []
# for _ in range(10):
#     if __name__ == '__main__':
#         p = multiprocessing.Process(target=sleeping)
#         p.start()
#         processes.append(p)
# for proc in processes:
#     proc.join()

# Method 3

saveDir = "H:/Python/images/"
#sites = ['KTLX','KSRX']
sites = ['KTLX']
rs = RadarServer('http://tds-nexrad.scigw.unidata.ucar.edu/thredds/radarServer/nexrad/level2/S3/')

state_path = 'H:/Python/shapefiles/states/ne_10m_admin_1_states_provinces.shp'
county_path = 'H:/Python/shapefiles/counties/tl_2017_us_county.shp'
interstate_path = 'H:/Python/shapefiles/interstates/interstate_shapefile.shp'

shapefile_paths = [state_path,county_path,interstate_path]
########################################################################################################################
class RadScan:
    def __init__(self,data,time,angle,sweep,shapes,saveDir,site):
        self.data = data
        self.time = time
        self.angle = angle
        self.sweep = sweep
        self.shapes = shapes
        self.saveDir = saveDir
        self.site = site

    def __str__(self):
        return f'Site: {self.site}\n' \
               f'Valid time: {self.time}\n' \
               f'Elv. Angle: {self.angle}\n' \
               f'Saving to: {self.saveDir}\n'
    def __call__(self):
        return self

########################################################################################################################
def raw_to_masked_float(var, data):
    # Values come back signed. If the _Unsigned attribute is set, we need to convert
    # from the range [-127, 128] to [0, 255].
    if var._Unsigned:
        data = data & 255

    # Mask missing points
    data = np.ma.array(data, mask=data==0)

    # Convert to float using the scale and offset
    return data * var.scale_factor + var.add_offset
########################################################################################################################
def polar_to_cartesian(az, rng):
    az_rad = np.deg2rad(az)[:, None]
    x = rng * np.sin(az_rad)
    y = rng * np.cos(az_rad)
    return x, y
########################################################################################################################
def getElvAngles(data):
    # Get the elevation angles
    angles = []
    for v in data.variables['elevationR_HI'][:]:
        angle = "%.1f" % v[-1]
        # adding a filter so that we're not collecting scans with minimal vertical difference
        if len(angles) == 0:
            angles.append(angle)
        else:
            if (float(angle) - float(angles[-1])) > 0.5:
                angles.append(angle)
    return angles


########################################################################################################################

def shapefile_read(path):
    # Read in the state shapefiles
    reader = shpreader.Reader(path)
    item = list(reader.geometries())
    return cfeature.ShapelyFeature(item, ccrs.PlateCarree())

########################################################################################################################
def plotRefl(scan):

    # get the range/az data
    rng = scan.data.variables['distanceR_HI'][:]
    az = scan.data.variables['azimuthR_HI'][scan.sweep]
    # convert the data from polar to cartesian
    az_rad = np.deg2rad(az)[:, None]
    x = rng * np.sin(az_rad)
    y = rng * np.cos(az_rad)

    # get reflectivity values
    ref_var = scan.data.variables['Reflectivity_HI']
    ref_data = ref_var[scan.sweep]
    # get the masked values

    # Values come back signed. If the _Unsigned attribute is set, we need to convert
    # from the range [-127, 128] to [0, 255].
    if ref_var._Unsigned:
        ref_data = ref_data & 255
    # Mask missing points
    ref_data = np.ma.array(ref_data, mask=ref_data == 0)
    # Convert to float using the scale and offset
    ref = ref_data * ref_var.scale_factor + ref_var.add_offset

    # Get plotting details
    LON = scan.data.StationLongitude
    LAT = scan.data.StationLatitude
    min = -55 # -60
    max = 90 # 85
    interval = 5
    ref_norm, ref_cmap = mpplots.ctables.registry.get_with_range('NWSStormClearReflectivity', min, max)
    title = f'{scan.site} {scan.angle} deg Reflectivity valid at {datetime.strftime(scan.time, "%m/%d/%Y %H:%M")} UTC'
    label = "dBZ"
    savename = saveDir + f'{scan.site}_{scan.angle}_refl_{datetime.strftime(scan.time, "%Y%m%d%H%M")}.png'

    proj = ccrs.LambertConformal(central_longitude=LON, central_latitude=LAT)
    fig = plt.figure(figsize=(10, 10))
    # New axes with the specified projection
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], projection=proj)
    ax.background_patch.set_facecolor('dimgray')

    # Add and style shapefile features
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), zorder=1)
    ax.add_feature(scan.shapes[1], facecolor='none', edgecolor='darkslategray', linewidth=0.75, alpha=0.7, zorder=2)
    ax.add_feature(scan.shapes[0], facecolor='none', edgecolor='k', linewidth=1.0, alpha=1.0, zorder=3)
    ax.add_feature(cfeature.LAKES, facecolor='lightsteelblue', linewidth=0.75, alpha=0.95, zorder=4)
    ax.add_feature(scan.shapes[2], facecolor='none', edgecolor='blue', linewidth=0.8, alpha=0.9, zorder=4)

    north = LAT + 2.0  # degrees
    south = LAT - 2.0  # degrees
    east = LON + 2.0  # degrees
    west = LON - 2.0  # degrees
    ax.set_extent((west, east, south, north))
    ax.set_aspect('auto')

    a = ax.pcolormesh(x, y, ref, cmap=ref_cmap, norm=ref_norm, zorder=0)

    cbar = fig.colorbar(a, orientation='horizontal', label=label, pad=0.00, aspect=50)
    cbar.ax.tick_params(labelsize=7)
    cbar.set_ticks(np.arange(min, max, interval))
    cbar.ax.set_xticklabels(np.arange(min, max, interval))

    fig.set_size_inches(10, 10)
    plt.suptitle(title, x=0.25, y=0.98, fontsize=12, fontweight=20, color='white')
    plt.savefig(savename, bbox_inches='tight')

########################################################################################################################

def plotVel(scan):

    # get the range/az data
    rng = scan.data.variables['distanceV_HI'][:]
    az = scan.data.variables['azimuthV_HI'][scan.sweep]
    # convert the data from polar to cartesian
    az_rad = np.deg2rad(az)[:, None]
    x = rng * np.sin(az_rad)
    y = rng * np.cos(az_rad)

    # get reflectivity values
    vel_var = scan.data.variables['RadialVelocity_HI']
    vel_data = vel_var[scan.sweep]
    # get the masked values

    # Values come back signed. If the _Unsigned attribute is set, we need to convert
    # from the range [-127, 128] to [0, 255].
    if vel_var._Unsigned:
        vel_data = vel_data & 255
    # Mask missing points
    vel_data = np.ma.array(vel_data, mask=vel_data == 0)
    # Convert to float using the scale and offset
    vel = vel_data * vel_var.scale_factor + vel_var.add_offset

    # Get plotting details
    LON = scan.data.StationLongitude
    LAT = scan.data.StationLatitude
    min = -55 # -60
    max = 90 # 85
    interval = 5
    vel_norm, vel_cmap = mpplots.ctables.registry.get_with_range('NWS8bitVel', min, max)
    title = f'{scan.site} {scan.angle} deg Velocity valid at {datetime.strftime(scan.time, "%m/%d/%Y %H:%M")} UTC'
    label = "knots"
    savename = saveDir + f'{scan.site}_{scan.angle}_vel_{datetime.strftime(scan.time, "%Y%m%d%H%M")}.png'

    proj = ccrs.LambertConformal(central_longitude=LON, central_latitude=LAT)
    fig = plt.figure(figsize=(10, 10))
    # New axes with the specified projection
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], projection=proj)
    ax.background_patch.set_facecolor('dimgray')

    # Add and style shapefile features
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), zorder=1)
    ax.add_feature(scan.shapes[1], facecolor='none', edgecolor='darkslategray', linewidth=0.75, alpha=0.7, zorder=2)
    ax.add_feature(scan.shapes[0], facecolor='none', edgecolor='k', linewidth=1.0, alpha=1.0, zorder=3)
    ax.add_feature(cfeature.LAKES, facecolor='lightsteelblue', linewidth=0.75, alpha=0.95, zorder=4)
    ax.add_feature(scan.shapes[2], facecolor='none', edgecolor='blue', linewidth=0.8, alpha=0.9, zorder=4)

    north = LAT + 2.0  # degrees
    south = LAT - 2.0  # degrees
    east = LON + 2.0  # degrees
    west = LON - 2.0  # degrees
    ax.set_extent((west, east, south, north))
    ax.set_aspect('auto')

    a = ax.pcolormesh(x, y, vel, cmap=vel_cmap, norm=vel_norm, zorder=0)

    cbar = fig.colorbar(a, orientation='horizontal', label=label, pad=0.00, aspect=50)
    cbar.ax.tick_params(labelsize=7)
    cbar.set_ticks(np.arange(min, max, interval))
    cbar.ax.set_xticklabels(np.arange(min, max, interval))

    fig.set_size_inches(10, 10)
    plt.suptitle(title, x=0.25, y=0.98, fontsize=12, fontweight=20, color='white')
    plt.savefig(savename, bbox_inches='tight')

########################################################################################################################

def plotRadar(site,shapes,valid_time):
    # Get the data
    query = rs.query()
    query.stations(site).time(valid_time)
    rs.validate_query(query)
    catalog = rs.get_catalog(query)
    data = catalog.datasets[0].remote_access()

    angles = getElvAngles(data)

    scans = [RadScan(data, valid_time, angles[sweep], sweep, shapes, saveDir, site) for sweep in range(0, len(angles))]

    for scan in scans:
        plotRefl(scan)
        plotVel(scan)



# with concurrent.futures.ProcessPoolExecutor() as executor:
#     if __name__ == '__main__':
#         # f1 = executor.submit(sleeping)
#         # print(f1.result())
#         # results = [executor.submit(sleeping) for _ in range(10)]
#         # for f in concurrent.futures.as_completed(results):
#         #     print(f.result())
#         # results = executor.map(sleeping)
#
#
#         # Get the shapefiles
#         shapes = [shapefile_read(p) for p in shapefile_paths]
#         valid_time = datetime.utcnow()
#         for site in sites:
#             executor.submit(plotRadar(site,shapes,valid_time))


#with concurrent.futures.ProcessPoolExecutor() as executor:
if __name__ == '__main__':
    processes = []
    shapes = [shapefile_read(p) for p in shapefile_paths]
    valid_time = datetime.utcnow()
    for site in sites:
        p = mp.Process(target=plotRadar, args=(site,shapes,valid_time))
        processes.append(p)
        p.start()
    for proc in processes:
        proc.join()
            #plotRadar(site, shapes, valid_time)
            #executor.submit(plotRadar(site, shapes, valid_time))

#if __name__ == '__main__':
    # Get the shapefiles
    #shapes = [shapefile_read(p) for p in shapefile_paths]
    # Get current time
    #valid_time = datetime.utcnow()
    # Plot images
    # for site in sites:
    #     executor.submit(plotRadar(site,shapes,valid_time))
    # site = sites[0]
    #
    # query = rs.query()
    # query.stations(site).time(valid_time)
    # rs.validate_query(query)
    # catalog = rs.get_catalog(query)
    # data = catalog.datasets[0].remote_access()
    #
    # angles = getElvAngles(data)
    # scans = [RadScan(data, valid_time, angles[sweep], sweep, shapes, saveDir, site) for sweep in range(0, len(angles))]

    #queue = mp.Queue()
    # refl_plots = [mp.Process(target=plotRefl,args=(scan,)) for scan in scans]
    #
    # for rp in refl_plots:
    #     rp.start()
    # for rp in refl_plots:
    #     rp.join()
    # for scan in scans:
    #     p = mp.Process(target=plotRefl,args=(scan,))
    #     p.start()
    #     p.join()


    # refl_plots = [executor.submit(plotRefl(scan)) for scan in scans]
    # vel_plots = [executor.submit(plotVel(scan)) for scan in scans]


########################################################################################################################




finish = time.perf_counter()

print(f'Elapsed Time: {round(finish-start,2)} seconds.')