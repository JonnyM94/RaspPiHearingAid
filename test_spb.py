import matplotlib.pyplot as plt
from scipy.io import wavfile
import numpy as np
import timeit

from spb import *
from utilities import *

""" Load sample file """

fs,x = wavfile.read('runninga_20s.wav') # Open file
chunk = 128 # Buffer size
x = x[0:chunk-1] # Limit to buffer size
x = pcm2float(x) # Convert to float
t = np.arange(0,len(x))/fs # Generate time vector

""" Test gain """

fig1 = plt.figure(1)

G = -6

y = gain(x,G)

plt.plot(t,x)
plt.plot(t,y,'r')
plt.title('Gain of '+str(G)+' dB applied')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')

print('Gain = ' + str(np.average(timeit.repeat("gain(x,G)","from __main__ import gain,x,G",number=1,repeat=10000))*1000) + ' ms')

""" Test compressor """

fig2 = plt.figure(2)

tauA = 0.0001
tauR = 0.05
T = -10
CR = 2
KW = 10
MG = 0

y = compressor(x,fs,tauA,tauR,T,CR,KW,MG)

plt.plot(t,x)
plt.plot(t,y,'r')
plt.title('Envelope detection applied')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')

print('Compressor = ' + str(np.average(timeit.repeat("compressor(x,fs,tauA,tauR,T,CR,KW,MG)","from __main__ import compressor,x,fs,tauA,tauR,T,CR,KW,MG",number=1,repeat=10000))*1000) + ' ms')