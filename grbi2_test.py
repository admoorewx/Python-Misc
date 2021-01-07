import urllib
import xarray as xr

def getCompositeRefl():
    # Function: Retrieves the most recent CONUS composite reflectivity image from the IA State mesonet server.
    # This function will download a netCDF file of the radar data and save it locally, read in the data, and parse it
    # through Metpy. Returns an array of lons (x), lats (y), and radar data (dat) ready for plotting.

    radarURL = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/rap/prod/rap.20210105/rap.t01z.awip32f00.grib2"
    urllib.request.urlretrieve(radarURL, "rap.grib2")
    # get the radar data
    ds = xr.open_dataset("rap.grib2", engine='cfgrib')
    x = ds.variables['lon'][:]
    y = ds.variables['lat'][:]

    return x,y

x,y = getCompositeRefl()
print(x)