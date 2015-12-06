import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

def gain(x,gdB):
	y = np.multiply(np.power(10,gdB/20.0),x)
	return y

def add_feedback(input_signal,previous_output,gain):
    return np.add(input_signal,np.multiply(previous_output,gain))
	
def create_filters(filter_freq, order):
    "This returns a nnumber of filters, filter 1 = b[0],a[0] etc"
    b=[]
    a=[]
    
    for i in range(0,int(len(filter_freq)/2)):  #For every cutoff freq. pair
        f = [filter_freq[i*2],filter_freq[i*2 +1]]; #Get the pair
        bb, aa = signal.butter(order, f, 'bandpass') #Design a filter
        b.append(bb) #Append this to a list to return
        a.append(aa)
        
    return b,a


def plot_filter(b,a):
    "This plots the frequency response of a digital filter given by b and a"#
    
    w, h = signal.freqz(b, a) #Calculate response
    w_fix = [i/3.14 for i in w] #Use 0-1 instead of 0-pi
    plt.plot(w_fix, 20 * np.log10(abs(h))) #Plot it
    plt.xlim([0,1])
    plt.title('Butterworth filter frequency response')
    plt.xlabel('Frequency [pi*radians / second]')
    plt.ylabel('Amplitude [dB]')
    plt.margins(0, 0.1)
    plt.grid(which='both', axis='both')
    plt.show()

def plot_all_filters(b,a):
    "This plots the frequency response of a digital filter given by b and a"#

    for i in range(0,len(b)):
        w, h = signal.freqz(b[i], a[i]) #Calculate response
        w_fix = [i/3.14 for i in w] #Use 0-1 instead of 0-pi
        plt.plot(w_fix, 20 * np.log10(abs(h))) #Plot it
        
    plt.xlim([0,1])
    plt.title('Butterworth filter frequency response')
    plt.xlabel('Frequency [pi*radians / second]')
    plt.ylabel('Amplitude [dB]')
    plt.margins(0, 0.1)
    plt.grid(which='both', axis='both')
    plt.show()
