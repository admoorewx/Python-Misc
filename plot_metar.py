#!/usr/bin/python
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from matplotlib.dates import DateFormatter
import numpy as np
from Metars import METAR, singleMetar
import datetime
import sys



def plot(site,previous):
    metar = singleMetar(site,previous)
    temps = metar.temps
    dewps = metar.dewps
    wdir = metar.wdirs
    wspd = metar.wspds
    gust = metar.gusts
    visb = metar.vis
    pres = metar.press
    precip = metar.precip
    times = metar.times
    times = [datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ") for time in times]

    ### Filtering an other functions ###
    # filter the press for bad obs
    pres = np.asarray(pres)
    pres = np.where(pres < 500, np.nan, pres)

    # Get rainfall accumulations
    plot_precip = []
    accum = 0
    for p in precip:
        accum = accum + p
        plot_precip.append(accum)

    # set plotting parameters
    rot = 0
    ftsize = 8

    # Plot the temperature/dewpoint
    fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5)
    fig.set_size_inches(9,10)
    ax1.fill_between(times,-60,temps,facecolor='r',alpha=0.25)
    ax1.fill_between(times,-60,dewps,facecolor='g',alpha=0.55)
    ax1.set_xlim(times[0],times[-1])
    ax1.plot_date(times,temps,linestyle='solid',marker="None",color='r')
    ax1.plot_date(times,dewps,linestyle='solid',marker='None',color='g')
    ax1.axhline(y=0.0,linestyle='solid',color='k')
    ax1.xaxis.set_major_formatter( DateFormatter('%d %H:%M'))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=rot, fontsize=7)
    ax1.set_ylim(np.nanmin(dewps)-3.0,np.nanmax(temps)+3.0)
    ax1.set_ylabel("T/Td (C)", fontsize=ftsize)
    ax1.grid()

    # Plot the wind speed and direction
    ax2.fill_between(times,0,wspd,facecolor='b',alpha=0.25)
    ax2.plot_date(times,wspd,linestyle='solid',marker='None',color='b')
    ax2.plot_date(times,gust,marker='x',color='k')
    ax2.xaxis.set_major_formatter( DateFormatter('%d %H:%M'))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=rot, fontsize=7)
    ax2.set_ylim(0,np.nanmax(gust)+5.0)
    ax2.set_xlim(times[0],times[-1])
    ax2.set_ylabel("Wind Speed\n(knots)", fontsize=ftsize)
    ax2.grid()

    ax2b = ax2.twinx()
    ax2b.plot_date(times,wdir,marker='o',markersize=4,color='y')
    ax2b.xaxis.set_major_formatter( DateFormatter('%d %H:%M'))
    ax2b.set_ylim(0,360)
    ax2b.set_xlim(times[0],times[-1])
    ax2b.set_yticks(np.arange(0,450,90))
    ax2b.set_ylabel("Wind Direction (deg)",fontsize=ftsize)

    ax3.fill_between(times,0,pres,facecolor='k',alpha=0.45)
    ax3.plot_date(times,pres,linestyle='solid',marker="None",color='k')
    ax3.xaxis.set_major_formatter( DateFormatter('%d %H:%M'))
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=rot, fontsize=7)
    ax3.set_ylabel("MSLP (mb)", fontsize=ftsize)
    ax3.set_ylim(np.nanmin(pres)-5.0,np.nanmax(pres)+5.0)
    ax3.set_xlim(times[0],times[-1])
    ax3.grid()


    ax4.fill_between(times,0,visb,facecolor='gray',alpha=0.50)
    ax4.set_xlim(times[0],times[-1])
    ax4.plot_date(times,visb,linestyle='solid',marker="None",color='dimgray')
    ax4.xaxis.set_major_formatter( DateFormatter('%d %H:%M'))
    plt.setp(ax4.xaxis.get_majorticklabels(), rotation=rot, fontsize=7)
    ax4.set_ylabel("Visibility (mi)", fontsize=ftsize)
    ax4.set_ylim(0,12)
    ax4.grid()


    ax5.fill_between(times,0,plot_precip,facecolor='green',alpha=0.35)
    ax5.set_xlim(times[0],times[-1])
    ax5.plot_date(times,plot_precip,linestyle='solid',marker="None",color='g')
    ax5.xaxis.set_major_formatter( DateFormatter('%d %H:%M'))
    plt.setp(ax5.xaxis.get_majorticklabels(), rotation=rot, fontsize=7)
    ax5.set_ylabel("Rainfall (in)", fontsize=ftsize)
    ax5.set_ylim(0,plot_precip[-1]+0.2)
    ax5.grid()
    ax5.set_xlabel("Day/Time (UTC)")

    fig.suptitle(str(previous)+"-Hour Meteogram for "+site)
    fig.subplots_adjust(hspace=0.25)
    plt.show()

plot(sys.argv[1],sys.argv[2])