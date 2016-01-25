""" FUTURE IMPORTS """
from __future__ import print_function, division, absolute_import, unicode_literals
import platform
import time

""" INITIAL USER INPUTS """

# Check if debug mode should be enabled
ui_gui = raw_input('Would you like to enable the GUI? [y/n] ')
if ui_gui == 'y':
        gui = True
else:
        gui = False

ui_debug = raw_input('Would you like to enable debugging? [y/n] ')
if ui_debug == 'y':
        debug = True
else:
        debug = False



""" DEBUGGING FUNCTIONS """

def print_debug(x):
        if debug == True:
                print('# ',x)



""" IMPORT PYTHON MODULES """

"""

os                      # For checking files
ConfigParser    # For reading and writing .ini files
alsaaudio               # For communicating with ALSA
threading               # For multi-threading
numpy                   # For scientific computing
spb                     # Signal processing blocks for hearing aid
Tkinter         # For building GUI
matplotlib              # For plotting graphs
        
"""

print_debug('Importing modules...')

import os, ConfigParser, threading, numpy as np, spb

if gui == True: # Only import is GUI is required
        import Tkinter as tk, matplotlib.pyplot as plt



""" CONFIG PARSER """

print_debug('Reading config files...')

cfg = ConfigParser.ConfigParser()
if os.path.isfile("config.ini"):
        cfg.read('config.ini') # Load 'config.ini', if it exists
elif os.path.isfile("defaults.ini"):
        cfg.read('defaults.ini') # Load 'defaults.ini'
else:
        print("No .ini files exist! Exiting...")
        exit()

print_debug('Assigning global variables...')



""" GET VALUES FROM CONFIG """

# Gain
GAIN = cfg.getfloat('gain','value')

# Envelope detection
ENV_A_TIME = cfg.getfloat('envelope detection','attack_time')
ENV_R_TIME = cfg.getfloat('envelope detection','release_time')

# Compressor
COMPRESSOR_T = cfg.getfloat('compressor','threshold')
COMPRESSOR_CR = cfg.getfloat('compressor','compression_ratio')
COMPRESSOR_MG = cfg.getfloat('compressor','makeup_gain')
COMPRESSOR_KW = cfg.getfloat('compressor','knee_width')

#Feedback simulation
FEEDBACK_DELAY = cfg.getfloat('feedback_simulation','sample_delay')
FEEDBACK_GAIN = cfg.getfloat('feedback_simulation','feedback_gain')

""" SET AUDIO PARAMETERS """

print_debug('Setting audio parameters...')

buffer_size = cfg.getint('i/o','buffer_size')
channels = cfg.getint('i/o','channels')
period_size = 2*channels # Period size (in bytes) for int16 x number of channels
chunk = int(buffer_size/period_size)
card = cfg.get('i/o','card')
fs = cfg.getint('i/o','fs')



""" SET INPUT AND OUTPUT """

if platform.system()!='Windows':  #Don't load ALSA stuff when testing on windows
        import alsaaudio

inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NORMAL,card)

inp.setchannels(channels)
inp.setrate(fs)
inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
inp.setperiodsize(chunk)

out = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK,alsaaudio.PCM_NORMAL,card)
out.setchannels(channels)
out.setrate(fs)
out.setformat(alsaaudio.PCM_FORMAT_S16_LE)
out.setperiodsize(chunk)

print_debug('Reticulating splines...')



""" I/O FUNCTION """

silence = chr(0)*channels*chunk*2


def playAudio():

	while not finish:
		if BYPASS['AUDIO'] == False:
			t1 = time.time()
			l,data = inp.read() # Find length and extract data from stream
			if l == chunk: # Check that the length
				data_proc = np.fromstring(data,dtype="int16")
				
				if BYPASS['GAIN'] == False:
					data_proc = spb.gain(data_proc,GAIN)
					
				
				if BYPASS['COMPRESSOR'] == False:
					data_proc = spb.compressor(data_proc,fs,ENV_A_TIME,ENV_R_TIME,T,CR,KW,MG)
					
					
				data_proc = np.array(data_proc,dtype="int16") #Converts back to original data type for output
				out.write(data_proc) #Output
				
				t2 = time.time()
				print ('Total passage time')
				print ((t2-t1)*1000)
			else:
				out.write(silence)
	else:
		pass
	time.sleep(0.0001)

        output_feedback = np.zeros(chunk*2)
    



""" BYPASS FUNCTIONS """

if gui == False:

        BYPASS = {
                        'AUDIO': False,
                        'GAIN':  False,
                        'FEEDBACK': False,
						'COMPRESSOR': False,
                        }
                        
elif gui == True:
		
	BYPASS = {
						'AUDIO': True,
						'GAIN':  True,
						'FEEDBACK': True,
						'COMPRESSOR': True,
						}

	global btn_toggle_audio, btn_toggle_gain, btn_toggle_feedback, btn_toggle_comp
        
	def toggle_audio(): 											#Toggle audio on/off
				global BYPASS
				if BYPASS['AUDIO'] == True:
						BYPASS['AUDIO'] = False
						btn_toggle_audio.config(text='Stop audio')
				elif BYPASS['AUDIO'] == False:
						BYPASS['AUDIO'] = True
						btn_toggle_audio.config(text='Start audio')
        
	def toggle_gain():											#Toggle gain func on/off
                global BYPASS
                if BYPASS['GAIN']  == True:
                        BYPASS['GAIN']  = False
                        btn_toggle_gain.config(text='Gain ON')
                else:
                        BYPASS['GAIN']  = True
                        btn_toggle_gain.config(text='Gain OFF')

	def toggle_comp():											#Toggle compressor on/off
				global BYPASS
				if BYPASS['COMPRESSOR'] == True:
						BYPASS['COMPRESSOR'] = False
						btn_toggle_comp.config(text='Compressor ON')
				else:
						BYPASS['COMPRESSOR'] = True
						btn_toggle_comp.config(text='Compressor OFF')

	def toggle_feedback():										#Toggle feedback on/off
                global BYPASS
                if BYPASS['FEEDBACK']  == True:
                        BYPASS['FEEDBACK']  = False
                        btn_toggle_feedback.config(text='Feedback ON')
                else:
                        BYPASS['FEEDBACK']  = True
                        btn_toggle_feedback.config(text='Feedback OFF')



""" GUI INTERFACING """

if gui == True:
        
		# Gain
		def get_gain(val):
			global GAIN
			GAIN = float(val)   
			
			
		# Compressor Threshold
		def get_T(val):
			global T
			T = float(val)
			
		# Compressor Makeup
		def get_MG(val):
			global MG
			MG = float(val)
			
		# Compressor Knee Width
		def get_KW(val):
			global KW
			KW = float(val)
			
		# Compressor Compression ratio
		def get_CR(val):
			global CR
			CR = float(val)


""" TKINTER GUI """

print_debug('Generating GUI...')

def GUI():

	
	global finish
	global BYPASS
	global btn_toggle_audio, btn_toggle_gain, btn_toggle_comp
	
	root=tk.Tk()
	
	""" Toggle Audio"""
	btn_toggle_audio = tk.Button(root, text='Start audio', command=toggle_audio)
	btn_toggle_audio.grid(row=0, column=0)

	""" Gain """
	slider_gain = tk.Scale(root,from_=-20,to=30,resolution=0.1,label='GAIN (dB)',orient='horizontal',command=get_gain,length=120)
	slider_gain.set(GAIN)
	slider_gain.grid(row=1, column=0)
	
	btn_toggle_gain = tk.Button(root, text="Gain OFF", command=toggle_gain)
	btn_toggle_gain.grid(row=2,column=0)

	""" Compressor """
	btn_toggle_comp = tk.Button(root, text="Compressor OFF", command=toggle_comp)
	btn_toggle_comp.grid(row=4, column=0)
	
	slider_comp_thresh = tk.Scale(from_=-20, to=50, resolution=0.1,label="Threshold (dB)", orient="horizontal",command=get_T,length=120)
	slider_comp_thresh.set(COMPRESSOR_T)
	slider_comp_thresh.grid(row=5, column=0)
	
	slider_comp_MG = tk.Scale(from_=0, to=40, resolution=0.5,label="Makeup Gain (dB)",orient="horizontal", command=get_MG,length=120)
	slider_comp_MG.set(COMPRESSOR_MG)
	slider_comp_MG.grid(row=6, column=0)
	
	slider_comp_KW = tk.Scale(from_=0, to =30, resolution=0.5, label="Knee Width", orient="horizontal", command=get_KW,length=120)
	slider_comp_KW.set(COMPRESSOR_KW)
	slider_comp_KW.grid(row=7,column=0)
	
	slider_comp_CR = tk.Scale(from_=1, to=50, resolution=0.1, label="Compression Ratio", orient="horizontal", command=get_CR,length=120)
	slider_comp_CR.set(COMPRESSOR_CR)
	slider_comp_CR.grid(row=9, column=0)
	
	root.mainloop()
	    
	finish = True




""" THREADING """

finish = False

t_GUI = threading.Thread(target=GUI)
t_GUI.start()

t_audio = threading.Thread(target=playAudio)
t_audio.start()

t_GUI.join()
t_audio.join()
