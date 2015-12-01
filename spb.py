import numpy as np

def gain(x,gdB):
	y = np.multiply(np.power(10,gdB/20.0),x)
	return y