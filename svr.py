
import yfinance as YF
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd


from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR, NuSVR

from functions import delta, RSI, momentum, running_average, preprocess, discretize_delta, normalize, root_mean_squared_error, yahoo_hist

def SVR_forecast(stock,period,interval):

    # # Get the data from the YF API
    year = yahoo_hist(stock,period=period,interval=interval)
    year = preprocess(year)


    y = np.asarray(year["Close"])
    X = np.asarray(year.index)

    start = 0
    end = len(y) - 24

    recs = []
    valid_forecasts = []
    error = []
    model_fits = []
    plt.figure()
    for i in range(0,100):
        X1, X2, y1, y2 = train_test_split(X[start:end], y[start:end],train_size=0.7)
        #model = SVR(kernel='rbf',tol=np.std(y), epsilon=np.var(y))
        model = NuSVR(kernel='rbf', tol=np.std(y))
        model.fit(X1.reshape(-1,1), y1)
        ypredict = model.predict(X2.reshape(-1,1))
        model_fit_error = root_mean_squared_error(y[X2],ypredict)
        model_fits.append(model_fit_error)
        forecast = model.predict(X[end:].reshape(-1,1))
        forecast_errors = [np.random.normal(loc=0.0,scale=(np.std(y)*(i/(5.0*len(forecast))))) for i in range(len(forecast))]
        forecast = forecast + forecast_errors
        score = root_mean_squared_error(y[end:],forecast)
        error.append(score)


        last_ind = np.where(X2 == np.nanmax(X2))[0]
        last_yp = ypredict[last_ind]
        window = len(forecast) - 19

        if np.abs(forecast[0]-y[end]) > (np.std(y) * 0.5): 
            color='b'
            valid_forecasts.append(-1)
        else: # Only get forecasts from the valid ensemble members. 
            color='g'
            valid_forecasts.append(1)
            for ff in forecast[window:]: 
                if (ff - last_yp) > 0.0: 
                    recs.append(1)
                else: 
                    recs.append(-1)



        plt.scatter(X2,ypredict,color='r', alpha=0.2)
        plt.plot(X[end:],forecast,color=color,alpha=0.2)

    if np.mean(valid_forecasts) > 0.2: 
        if np.mean(recs) > 0.5:
            recommend = "BUY"
            net = y[-1] - y[end]
        elif np.mean(recs) < -0.2: 
            recommend = "SELL"
            net = y[-1] - y[end]
        else: 
            recommend = "HOLD POSITION"
            net = 0.0
    elif np.var(model_fits) <= 0.008: 
        recommend = "HOLD POSITION (Model Overfit)"
        net = 0.0
    else: 
        recommend = "HOLD POSITION (Inaccurate Forecast)"
        net = 0.0

    plt.plot(X,y,color='k')
    plt.title(f'{stock} Forecast - Recommendation: {recommend}')
    plt.xlim(0,len(X))
    plt.ylim(0,1.2)
    plt.show()


    print(f'Produced {len(error)} forecasts for {stock}:')
    print(f'Forecast average RMSE: {np.mean(error)}')
    print(f'Model Fit Error Variance: {np.var(model_fits)}')
    print(f'Model Fit Error Std Deviation: {np.std(model_fits)}')
    print(f'{stock} Std Deviation: {np.std(y)}')
    print(f'{stock} Variance: {np.var(y)}')
    print(f'Mean Rec Value: {np.mean(recs)}')
    print(f'Recommendation: {recommend}\n')
    return net