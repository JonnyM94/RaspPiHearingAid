import numpy as np
import time

def mag2dB(x):
	y = 20*np.log10(x)
	return y

def dB2mag(x):
	y = np.power(10,x/20)
	return y

def gain(x,gdB):
	"""Applies decibel gain to a signal.
	
	ARGUMENTS
	x : array
		Input array.
	gdB : float
		Desired gain (in dB).
	
	RETURNS
	y : numpy.ndarray
		Array x with gain applied.
				
	"""
	y = np.multiply(np.power(10,gdB/20.0),x)
	return y
	
def compressor(x,fs,tauA,tauR,T,CR,KW,MG):
	"""Applies dynamic compression to the signal.
	
	ARGUMENTS
	x : array
		Input array.
	T : float
		Threshold of compressor (in dB).
	tauA : float
		Attack time (in seconds).
	tauR : float
		Release time (in seconds).
	
	RETURNS
	y : numpy.ndarray
		Compresse.
				
	"""
	
	# Extract envelope
	t1 = time.time()
	alphaA = np.exp(-1/(tauA*fs)) # Convert tauA and tauR (attack and release times) for use in algorithm
	alphaR = np.exp(-1/(tauR*fs))
	x_abs = abs(x)
	c = 0 # Dummy variable for incoming signal
	x_env = np.zeros(len(x))

	for i in range(0,len(x)):
		if x_abs[i] > c: # When next sample is increasing
			c = alphaA*c+(1-alphaA)*x_abs[i] # Attack
		else: # When next sample is decreasing
			c = alphaR*c+(1-alphaR)*x_abs[i] # Release
		x_env[i] = c # Assig new value to y

	# Compute gain
	xdB_env = mag2dB(x_env)
	xdB = mag2dB(x)
	y = np.zeros(len(x))
	
	# Temp variables to speed up 'for loop'
	temp1 = 2*(xdB_env-T)
	temp2 = 2*(abs(xdB_env-T))
	
	tloopS = time.time()
	for i in range(0,len(x)):
		
		if temp1[i] < -KW: # Below threshold
			y[i] = x[i]
			
		elif temp2[i] <= KW: # Within knee range)
			y[i] = x*dB2mag((1/CR-1)*np.power((xdB[i]-T+KW/2),2)/(2*KW))
			
		elif temp1[i] > KW: # Over threshold
			y[i] = (x[i]/CR)*dB2mag(T(1-1/CR))
	
	t2 = time.time()
	print ("Envelope time")
	print((tloopS-t1)*1000)
	print("Loop Time")
	print((t2-tloopS)*1000)
	
	return y,x_abs,x_env,xdB_env

from numpy import multiply, power, add

def gain(x,gdB):
	y = multiply(power(10,gdB/20.0),x)
	return y

def add_feedback(input_signal,previous_output,gain):
    return add(input_signal,multiply(previous_output,gain))
	

