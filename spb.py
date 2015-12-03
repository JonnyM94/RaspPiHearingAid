import numpy as np

def gain(x,gdB):
	y = np.multiply(np.power(10,gdB/20.0),x)
	return y

def add_feedback(input_signal,previous_output,gain):
    return np.add(input_signal,np.multiply(previous_output,gain))
	
