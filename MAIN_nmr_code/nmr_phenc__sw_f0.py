'''
Created on May 24, 2022

@author: David Ariando

'''

#!/usr/bin/python

import os
import time
from datetime import datetime
import pydevd
from scipy import signal
import matplotlib.pyplot as plt
import numpy as np

from nmr_std_function.data_parser import parse_csv_float2col
from nmr_std_function.data_parser import parse_simple_info
from nmr_std_function.nmr_class import nmr_system_2022
from nmr_std_function.ntwrk_functions import cp_rmt_file, cp_rmt_folder, exec_rmt_ssh_cmd_in_datadir
from nmr_std_function.nmr_functions import plot_echosum
from nmr_std_function.time_func import time_meas
from nmr_std_function.expts_functions import phenc


# get the current time
now = datetime.now()
datatime = now.strftime("%y%m%d_%H%M%S")

# create folder for measurements
data_parent_folder = 'D:\\NMR_DATA'
meas_folder = '\\sw_f0_'+datatime

# variables
expt_num = 0 # set to 0 for a single experiment
sav_fig = 1 # save figures
show_fig = 0  # show figures

# enable time measurement
tmeas = time_meas(True)

# instantiate nmr object
client_data_folder = data_parent_folder+'\\'+meas_folder
nmrObj = nmr_system_2022( client_data_folder )

# report time
tmeas.reportTimeSinceLast("### load libraries")

# import default measurement configuration
from sys_configs.phenc_conf_halbach_v03_230323 import phenc_conf_halbach_v03_230323
phenc_conf = phenc_conf_halbach_v03_230323()

# sweep frequency
val_center = phenc_conf.cpmg_freq
val_span = 0.01 # the span of the value, half of this value is negative to center, and half is positive to the center
val_npts = 11
val_sw = np.linspace(val_center-0.5*val_span,val_center+0.5*val_span,val_npts)

# modify the experiment parameters
phenc_conf.dconv_f = 0 # set the downconversion frequency local oscillator to be a fixed frequency. Therefore, the downconversion frequency is unrelated to the B1 frequency. If set to 0, then the downconversion frequency is just B1 excitation frequency
phenc_conf.gradz_volt = 0.1
phenc_conf.gradx_volt = 0.1
phenc_conf.gradz_len_us = 100
phenc_conf.gradx_len_us = 100
phenc_conf.enc_tao_us = 200

# perform reference scan
print("\n(Reference scan)" )
nmrObj.folder_extension = "\\ref"
phenc_conf.en_lcs_pchg = 1 # enable lcs precharging
phenc_conf.en_lcs_dchg = 0 # enable lcs discharging
expt_num = 0 # set to 0 for a single experiment
sav_fig = 1 # save figure for reference scan
show_fig = 1 # show figure for reference scan
_, _, _, _, _, _, _, theta_ref, _ = phenc (nmrObj, phenc_conf, expt_num, sav_fig, show_fig)

# post-processing parameters for the phase encoding imaging
nmrObj.folder_extension = ("") # remove the folder extension and use only the data directory to process the data
phenc_conf.en_ext_rotation = 1 # enable external reference for echo rotation
phenc_conf.thetaref = theta_ref # external parameter: echo rotation angle
phenc_conf.en_conj_matchfilter = 0 # disable conjugate matchfiltering because it will auto-rotate the data
phenc_conf.en_ext_matchfilter = 0 # enable external reference for matched filtering
phenc_conf.echoref_avg = 0 # echo_avg_ref # external parameter: matched filtering echo average
sav_fig = 1 # save figures
show_fig = 0  # show figures

# settings for measurements
phenc_conf.en_lcs_pchg = 0 # disable lcs precharging because the vpc is already precharged by the reference scan
phenc_conf.en_lcs_dchg = 0 # disable lcs discharging because the vpc has to maintain its voltage for next scan

# run the experiment sweep
for i,val_curr in enumerate(val_sw):
    
    if (i==len(val_sw)-1):
        phenc_conf.en_lcs_dchg = 1 # enable discharging at the last iteration to dump vpc voltage
    
    print("\t\t\t\texpt: %d/%d ----- f0 = %0.10f MHz" % (i,len(val_sw)-1,val_curr) )
    phenc_conf.cpmg_freq = val_curr
    expt_num = i
    phenc(nmrObj, phenc_conf, expt_num, sav_fig, show_fig)

tmeas.reportTimeSinceLast("### processing")

# clean up
nmrObj.exit()