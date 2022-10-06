'''
Created on June 10th 2022

@author: David Ariando
'''

#!/usr/bin/python

import os
from datetime import datetime
import pydevd
from scipy import signal
import matplotlib.pyplot as plt

from nmr_std_function.nmr_functions import compute_in_bw_noise
from nmr_std_function.nmr_class import nmr_system_2022
from nmr_std_function.ntwrk_functions import cp_rmt_file, cp_rmt_folder, exec_rmt_ssh_cmd_in_datadir


def init( client_data_folder ):

    # instantiate nmr object
    nmrObj = nmr_system_2022( client_data_folder )

    return nmrObj


def analyze( nmrObj, samp_freq, samples, vvarac, en_filt, min_freq, max_freq, tuning_freq, meas_bw_kHz, continuous, en_fig ):

    while True:
        nmrObj.noise( samp_freq, samples, vvarac )

        cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, nmrObj.client_data_folder, "noise.txt" )
        cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, nmrObj.client_data_folder, "acqu.par" )

        # compute_stats( min_freq, max_freq, data_folder, meas_folder[0], 'noise_plot.png', en_fig )
        compute_in_bw_noise( en_filt, meas_bw_kHz, tuning_freq, min_freq, max_freq, nmrObj.client_data_folder, 'noise_plot.png', en_fig )
        
        print("vvarac : ", vvarac, "\n")
        
        '''
        if (vvarac < 3.8):
                vvarac = vvarac + 0.1;
        else:
            vvarac = -4.9;
        '''
        
        if ( not continuous ):
            
            break


def exit( nmrObj ):
    nmrObj.exit()


# uncomment this line to debug the nmr noise code locally here
samp_freq = 4.08*4  # sampling frequency
samples = 100000  # number of points
vvarac = -1.55 # voltage for the preamp (more negative, more capacitance)
en_filt = False # enable post-processing filter to limit the measurement bandwidth
min_freq = 0.001  # in MHz
max_freq = 8.0  # in MHz
tuning_freq = 4.0 # hardware tuning frequency selector, using lookup table
meas_bw_kHz = 100 # downconversion filter bw
continuous = True  # continuous running at one frequency configuration
client_data_folder = "D:\\NMR_DATA"
en_fig = True
nmrObj = init( client_data_folder )
analyze( nmrObj, samp_freq, samples, vvarac, en_filt, min_freq, max_freq, tuning_freq, meas_bw_kHz, continuous , en_fig )
exit( nmrObj )