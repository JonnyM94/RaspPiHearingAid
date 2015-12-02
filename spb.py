import numpy as np

def amp2dB(x):
	y = 20*np.log10(x)
	return y

def dB2amp(x):
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
	xdB_env = amp2dB(x_env)
	xdB = amp2dB(x)
	ydB = np.zeros(len(x))
	for i in range(0,len(x)):
		if 2*(xdB_env[i]-T) < -KW: # Below threshold
			ydB[i] = xdB[i]
		elif 2*(abs(xdB_env[i]-T)) <= KW: # Within knee range
			ydB[i] = xdB[i]+(1/CR-1)*np.power((xdB[i]-T+KW/2),2)/(2*KW)
		elif 2*(xdB_env[i]-T) > KW: # Over threshold
			ydB[i] = T+(xdB[i]-T)/CR
	ydB = ydB+MG
	y = dB2amp(ydB)
	return y