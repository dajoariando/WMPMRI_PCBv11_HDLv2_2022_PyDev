'''
Created on August 6th 2024

@author: David Ariando

This sequence plots the ADC data where the data is coming from several channels.
For example, for 3 channels data, the data would be ordered this way:
The data order is d0_ch0 - d0_ch1 - d0_ch2 - d1_ch0 - d1_ch1 - d1_ch2 - d2_ch0 --- etc.
'''

#!/usr/bin/python

import os
from datetime import datetime
# import pydevd
from scipy import signal
import matplotlib.pyplot as plt

from nmr_std_function.nmr_functions import plot_noise_multch, plot_noise_multch_avg
from nmr_std_function.nmr_class import nmr_system_2022
from nmr_std_function.ntwrk_functions import cp_rmt_file, cp_rmt_folder, exec_rmt_ssh_cmd_in_datadir

import numpy as np

def init( client_data_folder ):

    # instantiate nmr object
    nmrObj = nmr_system_2022( client_data_folder )

    return nmrObj


def analyze( nmrObj, vvarac, samp_freq, samples, min_freq, max_freq, continuous, en_fig ):
    i = 0
    avg_meas = 10
    nrChannel = 2 # this should be read from the config file, instead of a parameter.
    specPwr_sum = np.zeros((samples,nrChannel),dtype=float)
    specPwr_avg = np.zeros((samples,nrChannel),dtype=float)
    while True:
        nmrObj.noise( samp_freq, samples, vvarac )

        cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, nmrObj.client_data_folder, "noise.txt" )
        cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, nmrObj.client_data_folder, "acqu.par" )

        i = i + 1
        
        #plot_noise_multch ( min_freq, max_freq, nmrObj.client_data_folder, 'noise_plot.png', en_fig )
        spectx, spectPwr = plot_noise_multch_avg ( min_freq, max_freq, nmrObj.client_data_folder, 'noise_plot.png', en_fig )
        
        specPwr_sum = specPwr_sum + spectPwr
        
        print("vvarac : ", vvarac, "\n")
        '''
        if (vvarac < 0.5):
            vvarac = vvarac + 0.1;
        else:
            vvarac = -4.9;
        #'''
        
        #======================
        #==Cheng==
        # calculate averaging
        specPwr_avg =  np.sqrt(specPwr_sum/i)
        fft_range = [i for i, value in enumerate( spectx ) if ( 
            value >= min_freq and value <= max_freq )]  # limit fft display
        fig = plt.figure(201)
        fig.clf()
        for ii in range (nrChannel):
            ax = fig.add_subplot(nrChannel, 1, ii+1)
            line1, = ax.plot( spectx[fft_range], specPwr_avg[:,ii][fft_range], 'b-', label = 'data', linewidth = 0.5 )            
        
        if ( not continuous ):
            
            break


def exit( nmrObj ):
    nmrObj.exit()


# import default measurement configuration and modify
from sys_configs.phenc_conf_halbach_v03_240810_oil import scan_config
phenc_conf = scan_config()

# uncomment this line to debug the nmr noise code locally here
samp_freq = 20  # sampling frequency
samples = 10000  # number of points
vvarac = phenc_conf.vvarac # voltage for the preamp (more negative, more capacitance)
min_freq = 1  # in MHz
max_freq = 6 # in MHz
continuous = True  # continuous running at one frequency configuration
client_data_folder = "D:/NMR_DATA"
en_fig = True
nmrObj = init( client_data_folder )
analyze( nmrObj, vvarac, samp_freq, samples, min_freq, max_freq, continuous, en_fig )
exit( nmrObj )
