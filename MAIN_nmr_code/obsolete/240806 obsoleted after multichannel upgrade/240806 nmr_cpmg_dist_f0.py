'''
Created on May 25, 2023

@author: David Ariando

This code sweeps f0 and plot the spectrum in the same window.

'''

#!/usr/bin/python

import os
import time
from datetime import datetime
import pydevd
from scipy import signal
import matplotlib.pyplot as plt
from matplotlib import get_backend
import numpy as np

from nmr_std_function.data_parser import parse_csv_float2col
from nmr_std_function.data_parser import parse_simple_info
from nmr_std_function.nmr_class import nmr_system_2022
from nmr_std_function.ntwrk_functions import cp_rmt_file, cp_rmt_folder, exec_rmt_ssh_cmd_in_datadir
from nmr_std_function.nmr_functions import plot_echosum
from nmr_std_function.time_func import time_meas
from nmr_std_function.expts_functions import cpmg


# get the current time
now = datetime.now()
datatime = now.strftime("%y%m%d_%H%M%S")

# create folder for measurements
data_parent_folder = 'D:\\NMR_DATA'
meas_folder = '\\cpmg_sw_f0_'+datatime

# import default measurement configuration
from sys_configs.phenc_conf_halbach_v06_230503_dopedwater import phenc_conf_halbach_v06_230503_dopedwater
phenc_conf = phenc_conf_halbach_v06_230503_dopedwater()

# variables
expt_num = 0 # set to 0 for a single experiment
sav_fig = 0 # save figures
show_fig = 0  # show figures

# sweep frequency
val_center = phenc_conf.cpmg_freq
val_span = 0.2 # the span of the value, half of this value is negative to center, and half is positive to the center
val_npts = 21
val_sw = np.linspace(val_center-0.5*val_span,val_center+0.5*val_span,val_npts)

# enable time measurement
tmeas = time_meas(True)

# instantiate nmr object
client_data_folder = data_parent_folder+'\\'+meas_folder
nmrObj = nmr_system_2022( client_data_folder )

# report time
tmeas.reportTimeSinceLast("### load libraries")

# create figure for kspace_asum and image_asum
plt.ion()
fig_num =65
fig = plt.figure(fig_num,figsize=(14,7))
plot_backend = get_backend()
mng = plt.get_current_fig_manager()
if plot_backend == 'TkAgg':
    # mng.resize(*mng.window.maxsize())
    mng.resize( 1200, 600 )
elif plot_backend == 'wxAgg':
    mng.frame.Maximize( True )
elif plot_backend == 'Qt4Agg':
    mng.window.showMaximized()
#plt.switch_backend('agg')


# modify the config
phenc_conf.en_fit = True
#phenc_conf.a_est = [20] # array of amplitude estimate for fitting
#phenc_conf.t2_est = [40e-3] # array of t2 estimate for fitting



# run the experiment
for i,val_curr in enumerate(val_sw):
    expt_num = i
    phenc_conf.cpmg_freq = val_curr # set the frequency to test
    asum_re, asum_im, a0, snr, T2, noise, res, theta, echo_avg, fpeak, spect, wvect = cpmg(nmrObj, phenc_conf, expt_num, sav_fig, show_fig)
    
    # process figure
    fig = plt.figure(fig_num)
    plt.plot(wvect/(2*np.pi)+phenc_conf.cpmg_freq, np.real(spect))
    
    plt.xlim([3.9,4.5]) # limit the frequency to be shown
    
    fig.canvas.draw()
    fig.canvas.flush_events()


plt.savefig( nmrObj.client_data_folder + '\\spect_sweep.png' )
tmeas.reportTimeSinceLast("### processing")

# clean up
nmrObj.exit()