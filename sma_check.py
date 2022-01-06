import numpy as np
from functions import running_average, zero_freq

def sma_check(data,s1,s2):
	sma1 = running_average(data,window_size=s1,fill=True)
	sma2 = running_average(data,window_size=s2,fill=True)
	diffs = sma1 - sma2 # find the differences
	inds = np.where(np.isnan(diffs) == False)[0] # filter out the nans
	diffs = diffs[inds] # get all real values
	switches = zero_freq(diffs) # count the number of switches
	sign = np.sign(diffs[-1]) # get the final sign
	if switches == 0: # in case of no switch
		return 0
	elif (switches % 2) == 0: # in case of switch back to original state
		return 0
	else: 
		return sign