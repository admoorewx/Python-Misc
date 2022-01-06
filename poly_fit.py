import matplotlib.pyplot as plt
import numpy as np


def poly_fit(Y):
	low = 3
	high = 13
	deltas = []
	X = np.arange(0,len(Y))
	future = [X[-1] + i for i in range(0,5)]
	colors=['r','orange','goldenrod','olive','green','b','navy','darkslateblue','purple','magenta']
	plt.figure()
	plt.plot(X,Y,color='k',marker='o',linestyle='',label="base")
	for i in range(low,high):
	    model = np.poly1d(np.polyfit(X,Y,i))
	    plt.plot(X,model(X),color=colors[i-low],label=str(i))
	    plt.plot(future,model(future),color=colors[i-low],linestyle='--')
	    for val in model(future):
	    	deltas.append(val)

	plt.xlim(0,future[-1])
	plt.legend()    
	plt.show()
	deltas = [Y[-1]-x for x in deltas]
	count = np.where(np.asarray(deltas) > 0.0)[0]
	perc_pos = len(count)/len(deltas)
	mean = np.mean(deltas)
	print(perc_pos)
	print(mean)
	print(np.median(deltas))
	# return perc_pos, mean



	