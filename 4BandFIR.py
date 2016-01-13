import alsaaudio, time, numpy
import threading
import Tkinter
from scipy import signal
from matplotlib import pyplot as plt
from scipy import weave


chunk = 128 # Buffer size (128/fs = 8ms)
channels = 2
card = 'plughw:1,0' # Audio input/output source
fs = 16000 # Sampling frequency


""" INPUT """
inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NORMAL,card)
inp.setchannels(channels)
inp.setrate(fs)
inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
inp.setperiodsize(chunk)

""" OUTPUT """
out = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK,alsaaudio.PCM_NORMAL,card)
out.setchannels(channels)
out.setrate(fs)
out.setformat(alsaaudio.PCM_FORMAT_S16_LE)
out.setperiodsize(chunk)

silence = chr(0)*channels*chunk*2 # silence work around for incorrect chunk size

""" FIR filter coefficients """
# not sure about number of taps ?
h = signal.firwin(chunk-1,[0.00375, 0.0125],window='hamming',pass_zero=False) # approx 30-100Hz
h2 = signal.firwin(chunk-1,[0.0125, 0.0625],window='hamming',pass_zero=False) # 100-500Hz
h3 = signal.firwin(chunk-1,[0.0625, 0.1125],window='hamming',pass_zero=False) # 500-900Hz
h4 = signal.firwin(chunk-1,[0.1125, 0.8],window='hamming',pass_zero=False) # 900-6000Hz


""" Basic FIR filter (linear buffer) in C """
def f2(h,inp,output,c):
    c_code = """
            int i, k;

            for (k = 0; k < N; k++) {
                double out = 0;
                for (i = N - 1; i > 0; i--) c[i] = c[i-1];
                c[0] = inp[k];
                for (i = 0; i < ntaps; i++) out += c[i]*h[i];

                output[k] = out;
            }
            return_val = 0;
            """
    return weave.inline(c_code,['N','ntaps','c','inp','output','h'],compiler='gcc')


""" Ring buffer FIR """
def f(h,inp,output,c,iptr):
    c_code = """
            int i, k, index;

            for (k = 0; k < N; k++) {
                double out = 0;
                c[iptr] = inp[k];
                index = iptr;
                for (i = 0; i < ntaps; i++) {
                    if (index < 0) index = N - 1;
                    out += c[(index)]*h[i];
                    index = index - 1;
                }
                iptr = (iptr + 1) % N;
                output[k] = out;
            }
            return_val = 0;
            """
    return weave.inline(c_code,['N','ntaps','c','inp','output','h','iptr'],compiler='gcc')



""" The global variable 'start' communicates
between the GUI & playback threads """

def callback1():
    global start
    start = 1 # start playback

def callback2():
    global start
    start = 0 # stop playback

def filter_callback():
    global filt
    if filt == 1:
        filt = 0
    else:
        filt = 1

""" Update gain values for frequency bands from sliders """
def update_gain1(val): # Band 1
    global gain1
    gain1 = val

def update_gain2(val): # Band 2
    global gain2
    gain2 = val

def update_gain3(val): # Band 3
    global gain3
    gain3 = val

def update_gain4(val): # Band 4
    global gain4
    gain4 = val


""" Main playback function """
def play():
    while not finish:
        if start == 1:
                l,data = inp.read()

                if l == chunk: # Avoid writing incorrect data length out
                    if filt == 1: # if filter parameter set to ON

                        t1 = time.time()
                        numpydata = numpy.fromstring(data, dtype = numpy.int16)


                        # Inserts output filter values into the above ouput arrays
                        # when the functions below are called (see above C_code)

                        """ RING BUFFER METHOD (about 1.1ms faster than linear) """
                        f(h,numpydata,output1,c1,iptr)
                        f(h2,numpydata,output2,c2,iptr)
                        f(h3,numpydata,output3,c3,iptr)
                        f(h4,numpydata,output4,c4,iptr)

                        """ LINEAR METHOD """
                        #f2(h,numpydata,output1,c1)
                        #f2(h2,numpydata,output2,c2)
                        #f2(h3,numpydata,output3,c3)
                        #f2(h4,numpydata,output4,c4)

                        # Get gain values from sliders
                        global gain1, gain2, gain3, gain4

                        # Apply gain to bands and sum back together
                        outFinal = float(gain1)*output1 + float(gain2)*output2 + \
                                   float(gain3)*output3 + float(gain4)*output4 #add bands back together


                        out.write(outFinal.astype(numpy.int16))
                        t2 = time.time()
                        t.append((t2-t1)*1000.0)
                    else:
                        numpydata = numpy.fromstring(data, dtype = numpy.int16)

                        out.write(numpydata)

                else:
                    out.write(silence)
        else:
            pass
        time.sleep(0.001)




""" GUI """
def TkinterGui():
    global finish, start, filt

    window = Tkinter.Tk()
    btn1 = Tkinter.Button(window, text="Play", command=callback1) # Play button
    btn1.pack()

    btn2 = Tkinter.Button(window, text="Stop", command=callback2) # Stop button
    btn2.pack()    #app = App(mainWindow)

    btn3 = Tkinter.Button(window, text="Toggle filter", command=filter_callback)
    btn3.pack()

    scale = Tkinter.Scale(orient='horizontal',from_=0, to=2, command=update_gain1, resolution=0.1)
    scale.pack()

    scale2 = Tkinter.Scale(orient='horizontal',from_=0, to=2, command=update_gain2, resolution=0.1)
    scale2.pack()

    scale3 = Tkinter.Scale(orient='horizontal',from_=0, to=2, command=update_gain3, resolution=0.1)
    scale3.pack()

    scale4 = Tkinter.Scale(orient='horizontal',from_=0, to=2, command=update_gain4, resolution=0.1)
    scale4.pack()

    window.mainloop()
    #When the GUI is closed set finish to "True"
    finish = True
    start = 0


""" Variable declaration before running """
###########################################

t = [] # append time taken to process (chunk*channels)

iptr = 0 # pointer for ring buffer FIR method

# Initialise outputs for frequency bands (FIR) 
output1 = numpy.zeros([1,chunk*channels])
output2 = numpy.zeros([1,chunk*channels])
output3 = numpy.zeros([1,chunk*channels])
output4 = numpy.zeros([1,chunk*channels])

# Initialise the summed output of frequency bands
outFinal = numpy.zeros([1,chunk*channels])

ntaps = len(h) # number of filter coefficients
N = chunk*channels # number of samples to be processed

# Initialise buffer for each frequency band
c1 = numpy.zeros([1,chunk*channels])
c2 = numpy.zeros([1,chunk*channels])
c3 = numpy.zeros([1,chunk*channels])
c4 = numpy.zeros([1,chunk*channels])


finish = False
start = 0
filt = 0
###########################################


""" Threading & Start """
GUI = threading.Thread(target=TkinterGui)
GUI.start()

Process = threading.Thread(target=play)
Process.start()

GUI.join()
Process.join()

