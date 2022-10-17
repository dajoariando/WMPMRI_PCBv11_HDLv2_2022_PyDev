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
from nmr_std_function.data_parser import parse_csv_float2col
from nmr_std_function.data_parser import parse_simple_info
from nmr_std_function.nmr_class import nmr_system_2022
from nmr_std_function.ntwrk_functions import cp_rmt_file, cp_rmt_folder, exec_rmt_ssh_cmd_in_datadir
from nmr_std_function.nmr_functions import plot_echosum
from nmr_std_function.nmr_functions import compute_multiple

# create folder for measurements
data_parent_folder = 'D:'
meas_folder = 'NMR_DATA'+'\\T2_220917_140744'
file_name_prefix = 'data_'
absdatapath = data_parent_folder+'\\'+meas_folder
if not os.path.exists(absdatapath):
    os.makedirs(absdatapath)

# variables
client_data_folder = absdatapath
en_fig = 1  # enable figure

# post-processing parameter
dconv_lpf_ord = 2  # downconversion order
dconv_lpf_cutoff_kHz = 200  # downconversion lpf cutoff
en_ext_param = 0 # enable external parameter for echo rotation and matched filtering
thetaref = 0 # external parameter: echo rotation angle
echoref_avg = 0 # external parameter: matched filtering echo average
ignore_echoes = 16 # ignore initial echoes for data processing

# instantiate nmr object
nmrObj = nmr_system_2022( client_data_folder )

compute_multiple( nmrObj, data_parent_folder, meas_folder, file_name_prefix, en_fig, en_ext_param, thetaref, echoref_avg, dconv_lpf_ord, dconv_lpf_cutoff_kHz, ignore_echoes )
    
