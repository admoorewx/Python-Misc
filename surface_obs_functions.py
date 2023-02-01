import os
import pandas as pd
import datetime as DT
import numpy as np

def find_closest_time(request_datetime,filepath,window=15):
	valid_inds = []
	valid_stations = []
	# read in the data as pandas dataframe
	df = pd.read_csv(filepath)
	# Get the dates/times from the df
	obstimes = df['valid']
	for i,time in enumerate(obstimes): 
		try:
			dtime = DT.datetime.strptime(time,"%Y-%m-%d %H:%M")
			diff = request_datetime - dtime
			if abs(diff.total_seconds()) < (window*60):
				if df['station'].values[i] not in valid_stations: 
					valid_inds.append(i)
					valid_stations(df['station'].values[i])
		except:
			pass
	return df.iloc[valid_inds]


def to_float(data):
	values = []
	for d in data:
		try: 
			values.append(float(d))
		except:
			values.append(np.nan)
	return values

def filter_by_bounds(df,extent):
	# expects extent to be an array of [east_lon, west_lon, south_lat, north_lat]
	buffer = 0.5 # degrees
	inds = np.where(np.asarray(to_float(df['lat'].values)) >= extent[2]+buffer)[0]
	df = df.iloc[inds]
	inds = np.where(np.asarray(to_float(df['lat'].values)) <= extent[3]-buffer)[0]
	df = df.iloc[inds]
	inds = np.where(np.asarray(to_float(df['lon'].values)) <= extent[0]-buffer)[0]
	df = df.iloc[inds]
	inds = np.where(np.asarray(to_float(df['lon'].values)) >= extent[1]+buffer)[0]
	df = df.iloc[inds]
	return df

def clean_variable(values):
	inds = np.where(np.asarray(values) != "M")[0]
	return inds

def clean_data(df):
	# Go through and find reports that have missing data. 
	# Clean air temp
	df = df.iloc[clean_variable(df['tmpf'].values)]
	# Clean dewp
	df = df.iloc[clean_variable(df['dwpf'].values)]
	# Clean wspd
	df = df.iloc[clean_variable(df['sknt'].values)]
	# Clean wdir
	df = df.iloc[clean_variable(df['drct'].values)]
	return df