from alpaca_trade_api.rest import REST, TimeFrame

from scipy import interpolate
from scipy.optimize import curve_fit, leastsq
from scipy.signal import correlation_lags, correlate
from scipy.stats import spearmanr

import datetime as DT
import yfinance as YF
import matplotlib.pyplot as plt
import numpy as np
import os
import seaborn as sns; sns.set()
import pandas as pd

from poly_fit import poly_fit
from functions import delta, RSI, momentum, running_average, discretize_delta, normalize, root_mean_squared_error, yahoo_hist
from sma_check import sma_check
from fred import getSeries
from svr import SVR_forecast


def plot_scatter(X,Y,xlabel,ylabel,title=""):
    plt.figure()
    plt.scatter(X,Y,marker='o',color='k')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(alpha=0.5)
    plt.show()

def plot_line(X,Y,xlabel,ylabel,title=""):
    plt.figure()
    plt.plot(X,Y,color='k')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(alpha=0.5)
    plt.show()

def plot_lines(Y1,Y2,xlabel,ylabel,title=""):
    plt.figure()
    plt.plot(np.arange(0,len(Y1)),Y1,color='k')
    plt.plot(np.arange(0,len(Y2)),Y2,color='b')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(alpha=0.5)
    plt.show()

def plot_histogram(Y):
    plt.figure()
    #plt.hist(Y,bins=np.arange(-10.0,10.0,0.5))
    plt.hist(Y)
    plt.show()



# fed_interest_rate = getSeries('DFF')
# sp500 = getSeries('SP500')

cash = 10.00
stocks = ["NUE","BBWI","HUM","MRO","LW","GPN","AAPL", "GOOG", "FORD", "TSLA", "ALL", "AFL", "AMD", "AON", "ADM", "T", "BIO", "BSX", "COF", "CSCO", "DAL"]

for stock in stocks: 
    net = SVR_forecast(stock,period="6mo",interval="1h")
    cash = cash + net
    print(f'\n NET CASH: ${cash}\n')
    