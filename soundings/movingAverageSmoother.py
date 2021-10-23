import numpy as np

def movingAverageSmooth(data,window):
    """
    Use a centered moving average to smooth the data. Note that a trailing mean is used for the ends.
    Except for the ends, the mean will use window+1 values from data.
    data - input array
    window - how many values to use to compute the centered mean
    """
    smoothed = []
    for i in range(len(data)):
        if i < window:
            subset = data[:i+window+1]
        elif i > len(data)-window:
            subset = data[i-window:]
        else:
            subset = data[i-window:i+window+1]
        smoothed.append(np.mean(subset))
    return smoothed


data = [1,3,5,6,3,19,23,5,3,4,9,12,10,9,12,11,8,4,2,1,2,1]
smoothed = movingAverageSmooth(data,2)
print(smoothed)