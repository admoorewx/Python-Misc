#!/usr/bin/python
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from matplotlib.dates import DateFormatter
import numpy as np
from Metars import METAR, singleMetar
from wx_utilities import knot2mph, C2F
import datetime
from datetime import timedelta
import sys
import os


def plot(site,previous):
    try:
        #savedir = os.getcwd()
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

        ### Filtering and unit conversions ###
        # filter the press for bad obs
        pres = np.asarray(pres)
        pres = np.where(pres < 500, np.nan, pres)

        wspd = [knot2mph(w) for w in wspd]
        gust = [knot2mph(g) for g in gust]
        temps = [C2F(t) for t in temps]
        dewps = [C2F(td) for td in dewps]

        # Get rainfall accumulations
        plot_precip = []
        accum = 0
        for P,p in enumerate(precip): # P = index, p = value

            if P == 0:
                accum = accum + p
                plot_precip.append(accum)
                previousTime = times[P]
            else:
                currentTime = times[P]
                deltaT = currentTime - previousTime
                deltaT = deltaT.total_seconds()
                if deltaT >= 3600.0:
                    accum = accum + p
                    plot_precip.append(accum)
                    previousTime = currentTime
                else:
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
        ax1.axhline(y=32.0,linestyle='--',color='b')
        ax1.xaxis.set_major_formatter( DateFormatter('%d %H:%M'))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=rot, fontsize=7)
        ax1.set_ylim(np.nanmin(dewps)-3.0,np.nanmax(temps)+3.0)
        ax1.set_ylabel("T/Td (F)", fontsize=ftsize)
        ax1.grid()

        # Plot the wind speed and direction
        ax2.fill_between(times,0,wspd,facecolor='b',alpha=0.25)
        ax2.plot_date(times,wspd,linestyle='solid',marker='None',color='b')
        ax2.plot_date(times,gust,marker='x',color='k')
        ax2.xaxis.set_major_formatter( DateFormatter('%d %H:%M'))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=rot, fontsize=7)
        try:
            ax2.set_ylim(0,np.nanmax(gust)+5.0)
        except:
            ax2.set_ylim(0,np.nanmax(wspd)+5.0)
        ax2.set_xlim(times[0],times[-1])
        ax2.set_ylabel("Wind Speed\n(mph)", fontsize=ftsize)
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

        endTime = datetime.datetime.strftime(times[-1],"%m/%d/%Y %H:%M")
        fig.suptitle(str(previous)+"-Hour Meteogram for "+site.upper()+"\n Ending at time "+endTime,fontsize=17)


        if len(sys.argv) > 1:
            plt.show()
        else:
            plt.savefig("metar.jpeg")
        return True
    except:
        return False


try:
    plot(sys.argv[1],sys.argv[2])
except:
    pass

#plot("KOKC",24)