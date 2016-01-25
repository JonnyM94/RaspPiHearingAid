import matplotlib.pyplot as plt
from scipy.io import wavfile
import numpy as np
import timeit

from spb import *

def pcm2float(x,dtype='float64'):
	"""Convert a PCM signal to floating point data with a range from -1 to 1.
	
	ARGUMENTS
	x : array
		Input array of integral type.
	dtype : data type, optional
		Desired (floating point) data type.
	
	RETURNS
	numpy.ndarray
		Normalised floating point data.
				
	"""
	x = np.asarray(x) # Convert to numpy array
	if x.dtype.kind not in 'iu': # Check that x is a signed (i) or unsinged (u) integer
		raise TypeError("'x' must be an array of integers")
	dtype = np.dtype(dtype) # Convert string to data type object
	if dtype.kind != 'f': # Check that dtype is a floating point type
		raise TypeError("'dtype' must be a floating point type")
	i = np.iinfo(x.dtype) # Find machine limits for data type
	abs_max = 2**(i.bits-1) # Find absolute max limits
	offset = i.min + abs_max # Find offset
	return (x.astype(dtype)-offset)/abs_max # Convert signal to floating point type

""" Load sample file """

fs,x = wavfile.read('runninga_20s.wav') # Open file
chunk = 2512 # Buffer size
x = x[2000:chunk-1] # Limit to buffer size
x = pcm2float(x) # Convert to float
t = np.arange(0,len(x))/fs # Generate time vector

""" Test gain """

fig1 = plt.figure(1)

G = -6

y = gain(x,G)

plt.plot(x)
plt.plot(y,'r')
plt.title('Gain of '+str(G)+' dB applied')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.show()

#print('Gain = ' + str(np.average(timeit.repeat("gain(x,G)","from __main__ import gain,x,G",number=1,repeat=100))*1000) + ' ms')

""" Test compressor """

fig2 = plt.figure(2)

tauA = 0.00001
tauR = 0.0001
T = -10
CR = 2
KW = 10
MG = 0

[y,x_abs,x_env,xdB_env] = compressor(x,fs,tauA,tauR,T,CR,KW,MG)

plt.plot(x)
plt.plot(x_env,'r')
plt.title('Envelope detection applied')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.show()

fig2 = plt.figure(3)

plt.plot(x)
plt.plot(y,'r')
plt.title('Compressed signal')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.show()

#print('Compressor = ' + str(np.average(timeit.repeat("compressor(x,fs,tauA,tauR,T,CR,KW,MG)","from __main__ import compressor,x,fs,tauA,tauR,T,CR,KW,MG",number=1,repeat=100))*1000) + ' ms')
