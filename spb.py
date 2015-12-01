import numpy as np

def gain(x,gdB):
	y = np.multiply(np.power(10,gdB/20.0),x)
	return y
	
def envelope_detection(x,fs,tauA,tauR): # Branching smooth envelope detection method
	alphaA = np.exp(-1/(tauA*fs)) # Convert tauA and tauR (attack and release time constants) to time
	alphaR = np.exp(-1/(tauR*fs))
	y = abs(x)
	c = 0 # Dummy variable for incoming signal
	for i in range(0,len(y)):
		if y[i] > c: # When next sample is increasing
			c = alphaA*c+(1-alphaA)*y[i] # Attack
		else: # When next sample is decreasing
			c = alphaR*c+(1-alphaR)*y[i] # Release
		y[i] = c # Assig new value to y
	return y

def compressor(x,T,CR,KW,MG):
	# Compute gain
	xdB = 20*np.log10(x)
	ydB = np.zeros(len(x))
	for i in range(0,len(xdB)):
		if 2*(xdB[i]-T) < -KW: # Below threshold
			ydB[i] = xdB[i]
		elif 2*(abs(xdB[i]-T)) <= KW: # Within knee range
			ydB[i] = xdB[i]+(1/CR-1)*np.power((xdB[i]-T+KW/2),2)/(2*KW)
		elif 2*(x[i]-T) > KW: # Over threshold
			ydB[i] = T+(xdB[i]-T)/CR
	y = np.power(10,ydB/20)
	return y