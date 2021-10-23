# Upper Air
from datetime import datetime, timedelta
from metpy.units import units
import matplotlib.pyplot as plt
import matplotlib.colors as Colors
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import metpy.plots as mpplots
import metpy.calc as mcalc
import numpy as np
import pandas as pd
import os

csv_dir = "H:/Python/Python-Misc/soundings/"

def getData(csvfile):
    df = pd.read_csv(csvfile)
    pressure = df['pressure'].values * units.hPa
    temp = df['temperature'].values * units.degC
    dewp = df['dewpoint'].values * units.degC
    u = df['u_wind'].values * units.meter/units.second
    v = df['v_wind'].values * units.meter/units.second
    hght = df['height'].values * units.meters
    return pressure,temp,dewp,u,v,hght

def getParcelInfo(type,p,t,td):
    if type == "mixed-layer":
        # define depth of ML parcel
        depth = 100.0 * units.hPa
        top_of_layer = (p[0] - depth) # get the top of the layer
        mid_layer = (p[0] - (depth/2.0)) # get the mid-point of the layer
        inds = np.where(p >= top_of_layer) # get all values within the layer
        temp = np.mean(t[inds]) # find the average temp
        dewp = np.mean(td[inds]) # find the average dewp
        inds = np.where(p <= mid_layer) # get the profile above the mid-layer point
        p = p[inds]
        t = t[inds]
        td = td[inds]
        p = np.insert(p,0,mid_layer) # add in the mid-level point so we can lift from this point
        t = np.insert(t,0,temp)
        td = np.insert(td,0,dewp)
        parcel_path = mcalc.parcel_profile(p,temp,dewp)
    elif type == "surface":
        parcel_path = mcalc.parcel_profile(p,t[0],td[0])
    else:
        print("ERROR: unkown parcel-type. Options are 'mixed-layer' or 'surface'.")
    # calculate the LCL, LFC, and EL
    lcl_p, lcl_t = mcalc.lcl(p[0],t[0],td[0])
    lfc_p, lfc_t = mcalc.lfc(p,t,td)
    el_p, el_t = mcalc.el(p,t,td)
    # find cape/cin
    cape, cin = mcalc.cape_cin(p,t,td, parcel_path)
    return parcel_path, p, t, lcl_p, lcl_t, lfc_p, lfc_t, el_p, el_t, cape, cin

def windColor(wspd):
    if wspd < 20.0:
        return 'cornflowerblue'
    elif wspd < 30.0:
        return 'steelblue'
    elif wspd < 40.0:
        return 'blue'
    elif wspd < 50:
        return 'navy'
    elif wspd < 75:
        return 'blueviolet'
    elif wspd < 100:
        return 'indigo'
    elif wspd < 150:
        return 'darkred'
    else:
        return 'magenta'

def virtualTemp(p,t,td):
    if t.units != units('degC'):
        t = t.to('degC')
        td = td.to('degC')
    if p.units != units('hPa'):
        p = p.to('hPa')
    # es = mcalc.saturation_vapor_pressure(t)
    e = mcalc.saturation_vapor_pressure(td)
    w = ((621.97 * (e/(p-e)))/1000.0).to('g/kg')
    return mcalc.virtual_temperature(t,w).to('degC')

def getDiff(pres,thetae):
    # Just get the numbers:
    pres = [p.magnitude for p in pres]
    pres = np.asarray(pres)
    # get the max temp in the lowest X mb:
    top_lower_layer = 700.0 # mb - Top of the bottom layer
    lower_layer_inds = [np.where(pres >= top_lower_layer)][0]
    max_temp = np.nanmax(thetae[lower_layer_inds])

    # get the min temp in the upper portion
    top_upper_layer = 100.0 # mb - where to stop looking for the min temp
    upper_layer_inds = [np.where(pres >= top_upper_layer)][0]
    #upper_layer_inds = [np.where(pres[upper_layer_inds] <= top_lower_layer)][0] # make sure to exclude the lower layer
    min_temp = np.nanmin(thetae[upper_layer_inds])

    diff = max_temp - min_temp
    return diff


def heightColors(hghts):
    colors = []
    for h in hghts:
        h = h.magnitude
        if h <= 3.0:
            colors.append('firebrick')
        elif h <= 6.0:
            colors.append('green')
        elif h <= 8.0:
            colors.append('b')
        else:
            colors.append('blueviolet')

def plotSounding(csv_dir,csvfile):
    # call getData
    file_loc = os.path.join(csv_dir,csvfile)
    p,t,td,u,v,hght = getData(file_loc)

    # data manipulation
    mask = p >= 100 * units.hPa

    wind_thin = 3 # thinning for wind barbs
    interval = np.asarray([100,150,200,250,300,350,400,450,500,550,600,625,650,675,700,750,800,825,850,875,900,925,950,975,1000]) * units.hPa
    idx = mcalc.resample_nn_1d(p,interval)
    wspds = mcalc.wind_speed(u[idx].to('knots'),v[idx].to('knots'))
    wind_colors = [windColor(w.magnitude) for w in wspds]

    # Get bulk shear values
    zero1BS = mcalc.bulk_shear(p, u, v, hght, depth=1000.0 * units.meter,bottom=hght[0])
    zero3BS = mcalc.bulk_shear(p,u,v,hght,depth=3000.0*units.meter,bottom=hght[0])
    zero6BS = mcalc.bulk_shear(p, u, v, hght, depth=6000.0 * units.meter,bottom=hght[0])
    # Note: the output unit says it's in m/s, but comparing to the SPC archived soundings, it
    # appears the magnitudes are actually in knots. Worth checking on again in the future.
    zero1BS = mcalc.wind_speed(zero1BS[0],zero1BS[1])
    zero3BS = mcalc.wind_speed(zero3BS[0], zero3BS[1])
    zero6BS = mcalc.wind_speed(zero6BS[0], zero6BS[1])

    # Find the theta-e Deficit:
    thetae = mcalc.equivalent_potential_temperature(p, t, td)
    theta_deficit = getDiff(p,thetae)


    # Establish figure
    fig = plt.figure(figsize=(12,12),tight_layout=True)
    skew = mpplots.SkewT(fig,rotation=45)


    # Parcel settings
    parcelType = "surface"
    tv = virtualTemp(p,t,td)
    parcel_path, parcel_p, parcel_t, lcl_p, lcl_t, lfc_p, lfc_t, el_p, el_t, cape, cin = getParcelInfo(parcelType,p,tv,td)
    # Plot data
    skew.plot(p,t,'r')
    skew.plot(p,td,'g')
    skew.plot(p,tv,'darkred',linestyle='--',alpha=0.5)
    skew.plot_barbs(p[idx], u[idx], v[idx], length=6, barbcolor="k", xloc=1.05)
    # plot parcel path
    skew.plot(parcel_p,parcel_path,'gray')
    skew.shade_cape(parcel_p,parcel_t,parcel_path)
    skew.shade_cin(p,tv,parcel_path)

    # Plot settings
    skew.ax.set_ylim(1025,100)
    skew.ax.set_xlim(-30,50)
    skew.ax.set_ylabel("Pressure (hPa)")
    skew.ax.set_xlabel("T/Td (C)")

    # Add the relevant special lines to plot throughout the figure
    skew.plot_dry_adiabats(np.arange(233, 533, 20) * units.K,
                           alpha=0.25, color='orangered')
    skew.plot_moist_adiabats(np.arange(233, 400, 5) * units.K,
                             alpha=0.25, color='navy')
    skew.plot_mixing_lines(alpha=0.35,color='darkgreen')
    skew.ax.axvline(0*units.degC, alpha=0.35, color='cyan')


    # add LCL, LFC, EL if valid
    # if lcl_p:
    #     skew.ax.axhline(lcl_p, xmin=0.85, xmax=0.9, color='g')
    #     #skew.ax.text(x=lcl_t,y=(lcl_p-(3.0*units.hPa)), s="LCL",color='g')
    # if lfc_p:
    #     skew.ax.axhline(lfc_p, xmin=0.85, xmax=0.9, color='r')
    #     #skew.ax.text(x=lfc_t,y=(lfc_p-(3.0*units.hPa)), s="LFC", color='r')
    # if el_p:
    #     skew.ax.axhline(el_p, xmin=0.85, xmax=0.9, color='b')
    #     #skew.ax.text(x=el_t,y=(el_p-(3.0*units.hPa)), s="EL", color='b')

    # Add a title
    station = csvfile[0:3]
    date = datetime.strptime(csvfile[4:-4],"%m%d%Y%H")
    plt.title('{} Sounding'.format(station), loc='left',fontsize=18)
    plt.title(datetime.strftime(date,"%m/%d/%Y %H UTC"), loc='right',fontsize=18)

    # Add text info
    parcelText = f'--- Thermodynamic Parameters ---\n' \
                 f'Parcel Type: {parcelType}\n' \
                 f'LCL: {round(lcl_p.magnitude, 2)} hPa | {round(lcl_t.magnitude,2)} C\n' \
                 f'LFC: {round(lfc_p.magnitude, 2)} hPa | {round(lfc_t.magnitude, 2)} C\n' \
                 f'EL:   {round(el_p.magnitude, 2)} hPa | {round(el_t.magnitude, 2)} C\n' \
                 f'CAPE: {round(cape.magnitude,2)} J/kg\n' \
                 f'CIN: {round(cin.magnitude,2)} J/kg\n' \
                 f'Theta-e Deficit: {round(theta_deficit.magnitude, 2)} K\n' \
                 f'\n'\
                 f'--- Shear Parameters ---\n' \
                 f'0-1 km Bulk Shear: {round(zero1BS.magnitude, 2)} knots\n' \
                 f'0-3 km Bulk Shear: {round(zero3BS.magnitude,2)} knots\n' \
                 f'0-6 km Bulk Shear: {round(zero6BS.magnitude,2)} knots\n' \

    axt = inset_axes(skew.ax, '30%', '30%', loc=3)
    axt.text(0.0,0.0,parcelText,fontsize=13)
    axt.axis('off')


    # insert the hodograph
    ax_hod = inset_axes(skew.ax, '30%', '30%', loc=1)
    h = mpplots.Hodograph(ax_hod,component_range=60.)
    h.add_grid(increment=10)
    hodo_inds = np.where(p >= 100.0*units.hPa)[0]
    h.plot_colormapped(u[hodo_inds],v[hodo_inds],hght[hodo_inds],cmap=plt.get_cmap('jet'),norm=Colors.Normalize(vmin=0.0,vmax=12000.0))

    plt.tight_layout()
    plt.savefig(os.path.join(csv_dir,station+"_"+datetime.strftime(date,"%m%d%Y%H")+"_snd.png"))
    #plt.show()


for filename in os.listdir(csv_dir):
    if filename.endswith(".csv"):
        plotSounding(csv_dir,filename)