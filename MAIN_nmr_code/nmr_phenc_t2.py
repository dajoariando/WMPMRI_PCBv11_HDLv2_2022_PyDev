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
from nmr_std_function.time_func import time_meas


# get the current time
now = datetime.now()
datatime = now.strftime("%y%m%d_%H%M%S")

# create folder for measurements
data_parent_folder = 'D:\\NMR_DATA'
meas_folder = '\\T2_'+datatime

# create folder for measurements
client_data_folder = data_parent_folder+'\\'+meas_folder
if not os.path.exists(client_data_folder):
    os.makedirs(client_data_folder)

# variables
sav_fig = 1 # save figures
show_fig = 1  # show figures
process_data = 1 # process the nmr data, otherwise it'll be skipped

# enable time measurement
tmeas = time_meas(True)

# instantiate nmr object
nmrObj = nmr_system_2022( client_data_folder )

# report time
tmeas.reportTimeSinceLast("### load libraries")

# import default measurement configuration
from sys_configs.phenc_conf_221015 import phenc_conf_221015
phenc_conf = phenc_conf_221015()

# run cpmg sequence
phenc_conf.gradz_volt = 0.1
phenc_conf.gradx_volt = 0.1
nmrObj.phenc_t2_iter(phenc_conf)

# report time
tmeas.reportTimeSinceLast("### cpmg acquisition")

# process data
if ( process_data ):
    # copy files
    cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, nmrObj.client_data_folder, "datasum.txt" )
    cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, nmrObj.client_data_folder, "acqu.par" )
    # plot_echosum( nmrObj, nmrObj.client_data_folder + "\\" + "datasum.txt", samples_per_echo, echoes_per_scan, show_fig )
    
    compute_multiple( nmrObj, phenc_conf, sav_fig, show_fig)

# report time
tmeas.reportTimeSinceLast("### processing")
