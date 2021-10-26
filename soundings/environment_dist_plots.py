from datetime import datetime, timedelta
from metpy.units import units
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import metpy.plots as mpplots
import metpy.calc as mcalc
import numpy as np
import pandas as pd
import os
import random


csv_dir = "/home/andrew/Research/soundings/"
save_dir = "/home/andrew/Research/images/"

def getData(csvfile):
	df = pd.read_csv(csvfile)
	pressure = df['pressure'].values
	temp = df['temperature'].values 
	dewp = df['dewpoint'].values 
	u = df['u_wind'].values
	v = df['v_wind'].values 
	hght = df['height'].values 

	hght, pressure, temp, dewp, u, v = cleanData(hght, pressure, temp, dewp, u, v)

	hght = hght * units.meters
	pressure = pressure * units.hPa
	temp = temp * units.degC
	dewp = dewp * units.degC
	u = u * units.knots
	v = v * units.knots
	return pressure,temp,dewp,u,v,hght


def cleanData(hght,pres,temp,dewp,u,v):
	inds = []
	for i in range(1,len(hght)):
		if pres[i] >= pres[i-1]:
			inds.append(i)
	hght = np.delete(hght,inds)
	temp = np.delete(temp,inds)
	dewp = np.delete(dewp,inds)
	pres = np.delete(pres,inds)
	u = np.delete(u,inds)
	v = np.delete(v,inds)
	return hght, pres, temp, dewp, u, v


def getParcelInfo(type,p,t,td):
    if type == "mixed-layer":
        # define depth of ML parcel
        depth = 100.0 * units.hPa
        top_of_layer = (p[0] - depth) # get the top of the layer
        mid_layer = (p[0] - (depth/2.0)) # get the mid-point of the layer
        inds = np.where(p >= top_of_layer) # get all values within the layer
        temp = np.mean(t[inds]) # find the average temp
        dewp = np.mean(td[inds]) # find the average dewp
        inds = np.where(p < mid_layer) # get the profile above the mid-layer point
        p = p[inds]
        t = t[inds]
        td = td[inds]
        p = np.insert(p,0,mid_layer) # add in the mid-level point so we can lift from this point
        t = np.insert(t,0,temp)
        td = np.insert(td,0,dewp)
        parcel_path = mcalc.parcel_profile(p,temp,dewp)
    elif type == "surface":
        parcel_path = mcalc.parcel_profile(p,t[0],td[0])
    elif type == "most-unstable":
    	thetae = mcalc.equivalent_potential_temperature(p,t,td)
    	ind = np.where(np.nanmax(thetae.magnitude))[0]
    	parcel_path = mcalc.parcel_profile(p,t[ind],td[ind])
    else:
        print("ERROR: unkown parcel-type. Options are 'mixed-layer' or 'surface'.")
    # find cape/cin
    cape, cin = mcalc.cape_cin(p,t,td, parcel_path)
    return cape, cin


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


def get_CAPEs(csvfile):
	# call getData
    p,t,td,u,v,hght = getData(csvfile)
    tv = virtualTemp(p,t,td)

    # get surface-based CAPE
    parcelType = "surface"
    sbcape, sbcin = getParcelInfo(parcelType,p,tv,td)

    # get mixed-layer CAPE:
    parcelType = "mixed-layer"
    mlcape, mlcin = getParcelInfo(parcelType,p,tv,td)

    # get most-unstable CAPE:
    parcelType = "most-unstable"
    mucape, mucin = getParcelInfo(parcelType,p,tv,td)

    return [sbcape, mlcape, mucape, sbcin, mlcin, mucin]

    
def getShear(csvfile):
    p,t,td,u,v,hght = getData(csvfile)
    depth = 6000.0 * units.meters # layer dept in meters
    us, vs = mcalc.bulk_shear(p,u,v,height=hght,depth=depth)
    shear_mag = mcalc.wind_speed(us,vs)
    return shear_mag.magnitude

def get_effective_bulk_shear(csvfile):
    p,t,td,u,v,hght = getData(csvfile)
    # get the effective inflow layer
    eff_layer = effective_inflow_layer(p,t,td)
    if len(eff_layer) > 0:
        # get the bottom of the effective inflow layer
        eff_bottom = eff_layer[0]
        # get the most-unstable parcel profile
        thetae = mcalc.equivalent_potential_temperature(p,t,td)
        ind = np.where(np.nanmax(thetae.magnitude))[0]
        parcel_path = mcalc.parcel_profile(p,t[ind],td[ind])
        # need to get half the height of the mu parcel path and then find bulk shear
        # Find the EL pressure/temp
        el_p, el_t = mcalc.el(p,t,td,parcel_path)
        # get the index of the EL pres - do this by finding the smallest diff between P levels and EL_P
        diffs = [np.abs(P.magnitude - el_p.magnitude) for P in p]
        el_ind = diffs.index(np.min(diffs))
        # get the index of the bottom of the eff. inflow layer
        eff_ind = np.where(p == eff_bottom)[0][0]
        # get the depth of the layer
        depth = p[eff_ind] - p[el_ind]
        # find the eff bulk wind shear
        us,vs = mcalc.bulk_shear(p,u,v,bottom=p[eff_ind],depth=depth)
        shear_mag = mcalc.wind_speed(us,vs)
        return shear_mag.magnitude # Gives the shear in knots
    else:
        return 0.0 # Return an effective bulk wind shear value of 0.0 knots if there is not eff. layer

def effective_inflow_layer(p,t,td):
    tv = virtualTemp(p,t,td)
    min_cape = 100.0 * units('J/kg')
    min_cin = -250.0 * units('J/kg')
    parcel_paths = [mcalc.parcel_profile(p,tv[i],td[i]) for i in range(0,len(p))]
    inds = []
    for path in parcel_paths:
        cape,cin = mcalc.cape_cin(p,tv,td,path)
        if cape >= min_cape and cin >= min_cin: 
            inds.append(np.where(tv == path[0])[0][0])
    return p[inds]
 

def plot_cape_shear(capes,shears):
    get_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF),range(n)))
    colors = get_colors(len(shears))

    plt.figure(1)
    for i in range(0,len(shears)):
        # plot the capes
        #plt.scatter(shears[i],capes[i][0],color=colors[i],marker='o')
        plt.scatter(shears[i],capes[i][1],color=colors[i],marker='o')
        #plt.scatter(shears[i],capes[i][2],color=colors[i],marker='v')
        # plot the cins
        #plt.scatter(shears[i],capes[i][3],color=colors[i],marker='o')
        plt.scatter(shears[i],capes[i][4],color=colors[i],marker='x')
        #plt.scatter(shears[i],capes[i][5],color=colors[i],marker='v')

    plt.axhline(y=0,xmin=0,xmax=60,linestyle='--',color='k')
    plt.ylim(-500,4000)
    plt.xlim(0,60)
    plt.title("Sounding MLCAPE/MLCIN/Shear Space")
    plt.xlabel("Effective Bulk Wind Shear (knots)")
    plt.ylabel("MLCAPE/MLCIN (J/kg)")
    plt.grid(alpha=0.5,color='gray')

    plt.savefig(save_dir+"cape_cin_shear_dist.png")


    plt.figure(2)
    for i in range(0,len(shears)):
        # plot the capes
        #plt.scatter(shears[i],capes[i][0],color=colors[i],marker='o')
        plt.scatter(shears[i],capes[i][1],color=colors[i],marker='o')
        #plt.scatter(shears[i],capes[i][2],color=colors[i],marker='v')
    plt.ylim(0,4000)
    plt.xlim(0,60)
    plt.title("Sounding MLCAPE/Shear Space")
    plt.xlabel("Effective Bulk Wind Shear (knots)")
    plt.ylabel("MLCAPE (J/kg)")
    plt.grid(alpha=0.5,color='gray')
    plt.savefig(save_dir+"cape_shear_dist.png")


    plt.figure(3)
    for i in range(0,len(shears)):
        # plot the capes
        #plt.scatter(shears[i],capes[i][0],color=colors[i],marker='o')
        plt.scatter(shears[i],capes[i][4],color=colors[i],marker='o')
        #plt.scatter(shears[i],capes[i][2],color=colors[i],marker='v')
    plt.ylim(-300,0)
    plt.xlim(0,60)
    plt.title("Sounding MLCAPE/Shear Space")
    plt.xlabel("Effective Bulk Wind Shear (knots)")
    plt.ylabel("MLCAPE (J/kg)")
    plt.grid(alpha=0.5,color='gray')
    plt.savefig(save_dir+"cin_shear_dist.png")


capes = []
shears = []
for filename in os.listdir(csv_dir):
    csvfile = os.path.join(csv_dir,filename) 
    capes.append(get_CAPEs(csvfile))
    shears.append(get_effective_bulk_shear(csvfile))

plot_cape_shear(capes,shears)

