""" FUTURE IMPORTS """

from __future__ import print_function, division, absolute_import, unicode_literals
import platform


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

chunk = cfg.getint('i/o','chunk')
channels = cfg.getint('i/o','channels')
card = cfg.get('i/o','card')
fs = cfg.getint('i/o','fs')



""" SET INPUT AND OUTPUT """

if platform.system()!='Windows':  #Don't load ALSA stuff when testing on windows
        import alsaaudio

        print_debug('Reticulating splines...')

        inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NORMAL,card)
        inp.setchannels(channels)
        inp.setrate(fs)
        inp.setformat(alsaaudio.PCM_FORMAT_FLOAT_LE)
        inp.setperiodsize(chunk)

        out = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK,alsaaudio.PCM_NORMAL,card)
        out.setchannels(channels)
        out.setrate(fs)
        out.setformat(alsaaudio.PCM_FORMAT_FLOAT_LE)
        out.setperiodsize(chunk)



""" I/O FUNCTION """

silence = chr(0)*channels*chunk*2


def playAudio():
        output_feedback = np.zeros(chunk*2)
        
        while not finish:
                if BYPASS['AUDIO'] == False:
                        l,data = inp.read() # Find length and extract data from stream
                        if l == chunk: # Check that the length
                                data_proc = np.fromstring(data,dtype="float32")

                                if BYPASS['FEEDBACK'] == False: #Add last output to current input
                                        data_proc = spb.add_feedback(data_proc,output_feedback,FEEDBACK_GAIN)

                                if BYPASS['GAIN'] == False:
                                        data_proc = spb.gain(data_proc,GAIN)

                                if BYPASS['FEEDBACK'] == False:  #Store the output buffer for feedback
                                        output_feedback = data_proc
                                        
                                data_out = np.array(data_proc,dtype="float32")
                                out.write(data_out)
                        else:
                                out.write(silence)
        else:
                pass
        time.sleep(0.001)



""" BYPASS FUNCTIONS """

if gui == False:

        BYPASS = {
                        'AUDIO': False,
                        'GAIN':  False,
                        'FEEDBACK': False,
                        }
                        
elif gui == True:
        
        BYPASS = {
                        'AUDIO': True,
                        'GAIN':  True,
                        'FEEDBACK': True,
                        }
        
        global btn_toggle_audio, btn_toggle_gain, btn_toggle_feedback
        
        def toggle_audio():
                global BYPASS
                if BYPASS['AUDIO'] == True:
                        BYPASS['AUDIO'] = False
                        btn_toggle_audio.config(text='Stop audio')
                elif BYPASS['AUDIO'] == False:
                        BYPASS['AUDIO'] = True
                        btn_toggle_audio.config(text='Start audio')
        
        def toggle_gain():
                global BYPASS
                if BYPASS['GAIN']  == True:
                        BYPASS['GAIN']  = False
                        btn_toggle_gain.config(text='Gain ON')
                else:
                        BYPASS['GAIN']  = True
                        btn_toggle_gain.config(text='Gain OFF')

        def toggle_feedback():
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



""" TKINTER GUI """

print_debug('Generating GUI...')

def GUI():
        
        global finish
        global BYPASS
        global btn_toggle_audio, btn_toggle_gain, btn_toggle_feedback
        
        root=tk.Tk()
        
        btn_toggle_audio = tk.Button(root, text='Start audio', command=toggle_audio)
        btn_toggle_audio.pack()

        slider_gain = tk.Scale(root,from_=-20,to=6,resolution=0.1,label='GAIN',orient='horizontal',command=get_gain,length=120)
        slider_gain.set(GAIN)
        slider_gain.pack(fill='x')
        
        btn_toggle_gain = tk.Button(root, text="Gain OFF", command=toggle_gain)
        btn_toggle_gain.pack()

        btn_toggle_feedback = tk.Button(root, text="Feedback OFF", command=toggle_feedback)
        btn_toggle_feedback.pack()
        
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
